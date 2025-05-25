from sklearn.cluster import KMeans

def get_kmeans_clusters(features, n_clusters=10):
    model = KMeans(n_clusters=n_clusters, random_state=42)
    labels = model.fit_predict(features)
    return model, labels
