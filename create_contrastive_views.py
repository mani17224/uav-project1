import numpy as np


INPUT_FILE = "processed_data/transformer_normal_windows.npz"
OUTPUT_FILE = "processed_data/transformer_contrastive_views.npz"


def add_noise(x, noise_scale=0.02):
    noise = np.random.normal(
        loc=0.0,
        scale=noise_scale,
        size=x.shape
    ).astype(np.float32)

    return x + noise


def scale_features(x, scale_range=(0.98, 1.02)):
    scale = np.random.uniform(
        scale_range[0],
        scale_range[1],
        size=(1, x.shape[1])
    ).astype(np.float32)

    return x * scale


def create_view(x):
    x = add_noise(x)
    x = scale_features(x)
    return x.astype(np.float32)


def main():
    np.random.seed(42)

    data = np.load(INPUT_FILE)
    X = data["X"].astype(np.float32)

    view1 = np.array([create_view(x) for x in X])
    view2 = np.array([create_view(x) for x in X])

    np.savez_compressed(
        OUTPUT_FILE,
        view1=view1,
        view2=view2
    )

    print("========================================")
    print("CONTRASTIVE VIEWS CREATED")
    print("========================================")
    print("Original shape:", X.shape)
    print("View 1 shape:", view1.shape)
    print("View 2 shape:", view2.shape)
    print("View 1 NaN:", np.isnan(view1).sum())
    print("View 2 NaN:", np.isnan(view2).sum())
    print("Saved:", OUTPUT_FILE)


if __name__ == "__main__":
    main()
