import torch
import torch.nn as nn
from torch_geometric.nn import GATConv, global_mean_pool

class TSCH_NN(nn.Module):
    def __init__(self, node_feature_dim=20, out_dim=64, num_classes=3, dropout=0.5):
        super(TSCH_NN, self).__init__()

        # Model parameters
        N_Heads = 8
        hidden_dim1 = 128  # Increase the number of hidden layer nodes
        hidden_dim2 = 64
        hidden_dim3 = 32  # Increase the number of hidden layer nodes

        # GAT layers for IPv6 links
        self.GAT_ipv6 = GATConv(in_channels=node_feature_dim,
                                out_channels=out_dim,
                                heads=N_Heads,
                                dropout=dropout)

        # GAT layers for TSCH links
        self.GAT_tsch = GATConv(in_channels=node_feature_dim,
                                out_channels=out_dim,
                                heads=N_Heads,
                                dropout=dropout)

        # Additional GAT layer
        self.GAT_extra = GATConv(in_channels=out_dim,
                                 out_channels=out_dim,
                                 heads=N_Heads,
                                 dropout=dropout)

        # Feature fusion layers
        self.feature_fusion_ipv6 = nn.Linear(N_Heads * out_dim, hidden_dim1)
        self.feature_fusion_tsch = nn.Linear(N_Heads * out_dim, hidden_dim1)

        # More hidden layers
        self.hidden1 = nn.Linear(hidden_dim1 * 2, hidden_dim2)
        self.hidden2 = nn.Linear(hidden_dim2, hidden_dim3)
        self.hidden3 = nn.Linear(hidden_dim3, hidden_dim3)

        # Layers for predicting graph-level labels
        self.classifier_event = nn.Linear(hidden_dim3, num_classes)
        self.classifier_env = nn.Linear(hidden_dim3, num_classes)

        # Dropout layer
        self.dropout = nn.Dropout(dropout)

        # Initialize LeakyReLU activation function
        self.leakyrelu = nn.LeakyReLU(0.1)

        # L2 regularization
        self.l2_loss = nn.MSELoss()

    def forward(self, data):
        x = data.x
        batch = data.batch
        edge_index_ipv6 = data.edge_index_IPv6
        edge_attr_ipv6 = data.edge_attr_IPv6
        edge_index_tsch = data.edge_index_TSCH
        edge_attr_tsch = data.edge_attr_TSCH

        # Process node features through GAT layers
        nodes_ipv6 = self.GAT_ipv6(x, edge_index_ipv6)
        nodes_tsch = self.GAT_tsch(x, edge_index_tsch)

        # Reduce dimensions of node features before fusion
        nodes_ipv6 = self.feature_fusion_ipv6(nodes_ipv6)
        nodes_tsch = self.feature_fusion_tsch(nodes_tsch)

        # Feature fusion
        nodes_fused = torch.cat([nodes_ipv6, nodes_tsch], dim=-1)
        nodes_fused = self.leakyrelu(nodes_fused)

        # Additional hidden layers
        nodes_fused = self.leakyrelu(self.hidden1(nodes_fused))
        nodes_fused = self.dropout(nodes_fused)
        nodes_fused = self.leakyrelu(self.hidden2(nodes_fused))
        nodes_fused = self.dropout(nodes_fused)
        nodes_fused = self.leakyrelu(self.hidden3(nodes_fused))

        # Apply mean pooling to get graph-level features
        graph_features = global_mean_pool(nodes_fused, batch)

        # Predict graph-level labels
        out_event = self.classifier_event(graph_features)
        out_env = self.classifier_env(graph_features)

        # Calculate L2 regularization loss
        l2_loss = self.l2_loss(graph_features, torch.zeros_like(graph_features))

        # Return outputs and L2 regularization loss
        return out_event, out_env, l2_loss





