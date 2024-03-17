from parse import *
import pickle

log_with_opti = "/home/yanbo/contiki-ng/data/raw/2024-03-16_22-00-54.testlog"
log_without_opt = r"/home/yanbo/contiki-ng/data/raw/2024-03-16_14-59-54.testlog"
save_path = r"/home/yanbo/contiki-ng\ML\log1.pkl"


LP1 = LogParse(log_path=log_with_opti)
LP1.process()

AS1 = Analysis(LP1)
AS1.calculate_features()
AS1.calculate_loss_and_delay()

LP2 = LogParse(log_path=log_without_opt)
LP2.process()

AS1

# with open(save_path, "rb") as file:
#     LP1 = pickle.load(file)
#     AS1 = pickle.load(file)
#     LP2 = pickle.load(file)
#     AS2 = pickle.load(file)

with open(save_path,"wb") as file:
    pickle.dump(LP1, file)
    pickle.dump(AS1, file)
    pickle.dump(LP2, file)
    pickle.dump(AS2, file)



print(len(LP1.tsch_links))
print(len(LP2.tsch_links))

import matplotlib.pyplot as plt

# # delete the index that AS1.loss == 0
# delete_indexes = []
# for i in range(len(AS1.loss)):
#     if AS1.loss[i] != 0:
#         delete_indexes.append(i)

# AS1_L = [AS1.loss[i] for i in delete_indexes]
# AS2_L = [AS2.loss[i] for i in delete_indexes]
# AS1_D = [AS1.delay[i] for i in delete_indexes]
# AS2_D = [AS2.delay[i] for i in delete_indexes]


fig, axs = plt.subplots(2, 1)
fig.suptitle('Loss and Delay')
axs[0].plot(AS1.loss, label="with_opti")
axs[0].plot(AS2.loss, label="without_opti")

axs[0].set_title('Loss')
axs[0].legend()
axs[1].plot(AS1.delay, label="with_opti")
axs[1].plot(AS2.delay, label="without_opti")

axs[1].set_title('Delay')
axs[1].legend()
plt.show()