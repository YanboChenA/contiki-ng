from parse import *
import pickle

import matplotlib.pyplot as plt

with_orchestra_path = r"/home/yanbo/contiki-ng/data/raw/with_orchestra.testlog"
without_orchestra_path = r"/home/yanbo/contiki-ng/data/raw/without_orchestra.testlog"
with_orch_root_path = r"/home/yanbo/contiki-ng/data/raw/with_orchestra_root2.testlog"
save_path = r"/home/yanbo/contiki-ng/ML/log.pkl"

log_with_orchestra = LogParse(log_path=with_orchestra_path)
log_with_orchestra.process()
log_without_orchestra = LogParse(log_path=without_orchestra_path)
log_without_orchestra.process()

Analyser_with_orchestra = Analysis(log_with_orchestra)
Analyser_with_orchestra.calculate_features()
Analyser_with_orchestra.calculate_loss_and_delay()

Analyser_without_orchestra = Analysis(log_without_orchestra)
Analyser_without_orchestra.calculate_features()
Analyser_without_orchestra.calculate_loss_and_delay()


with open(save_path, "wb") as file:
    pickle.dump(log_with_orchestra, file)
    pickle.dump(log_without_orchestra, file)
    pickle.dump(Analyser_with_orchestra, file)
    pickle.dump(Analyser_without_orchestra, file)

# with open(save_path, "rb") as file:
#     log_with_orchestra = pickle.load(file)
#     log_without_orchestra = pickle.load(file)
#     Analyser_with_orchestra = pickle.load(file)
#     Analyser_without_orchestra = pickle.load(file)
#     log_with_orch_root = pickle.load(file)
#     Analyser_with_orch_root = pickle.load(file)

# Analyser_with_orch_root.calculate_loss_and_delay()

# log_with_orch_root = LogParse(log_path=with_orch_root_path)
# log_with_orch_root.process()
# Analyser_with_orch_root = Analysis(log_with_orch_root)
# Analyser_with_orch_root.calculate_features()

# with open(save_path, "wb") as file:
#     pickle.dump(log_with_orchestra, file)
#     pickle.dump(log_without_orchestra, file)
#     pickle.dump(Analyser_with_orchestra, file)
#     pickle.dump(Analyser_without_orchestra, file)
#     pickle.dump(log_with_orch_root, file)
#     pickle.dump(Analyser_with_orch_root, file)



# In same figure, show two subplots, one is loss, the other is delay
fig, axs = plt.subplots(2, 1)
fig.suptitle('Loss and Delay')
axs[0].plot(Analyser_with_orchestra.loss, label="with_orchestra")
axs[0].plot(Analyser_without_orchestra.loss, label="without_orchestra")
# axs[0].plot(Analyser_with_orch_root.loss, label="with_orchestra_root")
axs[0].set_title('Loss')
axs[0].legend()
axs[1].plot(Analyser_with_orchestra.delay, label="with_orchestra")
axs[1].plot(Analyser_without_orchestra.delay, label="without_orchestra")
# axs[1].plot(Analyser_with_orch_root.delay, label="with_orchestra_root")
axs[1].set_title('Delay')
axs[1].legend()
plt.show()