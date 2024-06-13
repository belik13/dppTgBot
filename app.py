import os
import torch
import torch.nn as nn
import numpy as np
from sklearn.cluster import DBSCAN
from collections import defaultdict

# модель
class SimpleNN(nn.Module):
    def __init__(self, input_size):
        super(SimpleNN, self).__init__()
        self.fc1 = nn.Linear(input_size, 64)
        self.fc2 = nn.Linear(64, 32)
        self.fc3 = nn.Linear(32, 2)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = self.fc3(x)
        return x

#input_size - количество признаков данных
def new_model(input_size):
    model = SimpleNN(input_size)
    # параметры модели
    model_path = os.path.join('column_alignment_model.pth')
    model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
    model.eval()
    return model

def analyze_alignment(file_path, model, input_size):
    data = []
    coordinates = []
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            parts = line.strip().split()
            if len(parts) == input_size:
                point = np.array(parts, dtype=np.float32)
                data.append(point)
                coordinates.append(parts[:2])


    # объединение массивов NumPy в один массив для ускорения
    data_array = np.array(data, dtype=np.float32)

    # преобразование данных в тензор
    data_tensor = torch.tensor(data_array)
    #print(f"Shape of input data: {data_tensor.shape}")

    # получение прогнозов модели
    outputs = model(data_tensor)
    _, predicted = torch.max(outputs, 1)

    # кластеризация точек
    clustering = DBSCAN(eps=0.1, min_samples=2).fit(data)
    cluster_labels = clustering.labels_

    # соотнесение точек с их предсказаниями и кластерами
    cluster_predictions = defaultdict(list)
    for i, (prediction, label) in enumerate(zip(predicted.tolist(), cluster_labels)):
        cluster_predictions[label].append((coordinates[i], prediction))

    #  отчет
    # 1 - соосные, 2 - не соосные
    report = [0,0]
    for cluster_id, points in cluster_predictions.items():
        cluster_report = []
        for point, prediction in points:
            if prediction == 0:
                report[1] += 1
            else:
                report[0] += 1

    summ = sum(report)
    str_rep = f"{((report[0] / summ) * 100):.4f}% - Cоосны\n{((report[1] / summ) * 100):.4f}% - Не соосны\n"
    if ((report[0] / summ) * 100) < 20:
        str_rep += "Очень малая соосность"
    elif ((report[0] / summ) * 100) < 40:
        str_rep += "Малая соосность"
    elif ((report[0] / summ) * 100) < 60:
        str_rep += "Средняя соосность"
    elif ((report[0] / summ) * 100) < 80:
        str_rep += "Высокая соосность"
    else:
        str_rep += "Очень высокая соосность"

    return str_rep
