import pandas as pd
from posting_list import get_pst_list
from vgg16 import compute_image_features
from keras.preprocessing import image
from sklearn.metrics.pairwise import cosine_similarity


repository = 'Datathon-2023/'
image_path = repository + 'datathon/images/'

products = pd.read_csv(repository + 'products_clean.csv')
outfits = pd.read_csv(repository + 'datathon/dataset/outfit_data.csv')


features_df = compute_image_features()
pst_list = get_pst_list(outfits, products)


def get_nth_level_products(product: str, product_type: str, pst_list: dict):
    """
    """
    fst_level_products = []
    related_products = pst_list[product]['related_products']

    for p in related_products:
        p_pst_list = pst_list[p]['related_products']

        for p2 in p_pst_list:
            if p2 == product:
                pass
            p2_type = pst_list[p2]['type']
            if p2 not in fst_level_products and p2 not in related_products and product_type == p2_type:
                fst_level_products.append(p2)
    
    return fst_level_products


def img_similarity(image1: str, image2: str, show: bool = False) -> float:
    """
    Returns the cosine similarity between two images.

    Parameters
    ----------
    image1 : str
        Name of the first image.
    image2 : str
        Name of the second image.
    dir : str
        Directory of the images.
    show : bool
        Whether to display the images or not.

    Returns
    -------
    float
        Cosine similarity between the two images.
    """

    img1 = image.load_img(repository + image1)
    img2 = image.load_img(repository + image2)

    if show:
        display(img1, img2)

    image1 = image1.split('/')[-1]
    image2 = image2.split('/')[-1]
    
    features1 = features_df.loc[image1].values.reshape(1, -1)
    features2 = features_df.loc[image2].values.reshape(1, -1)

    similarity = cosine_similarity(features1, features2)

    return similarity[0][0]


def tab_similarity(product1: str, product2: str, beta: int = 0.9) -> float:
    """
    Returns the cosine similarity between two products from the products dataframe.

    Parameters
    ----------
    product1 : str
        Name of the first product.
    product2 : str
        Name of the second product.
    beta : int
        Weight of the color similarity.

    Returns
    -------
    float
        Cosine similarity between the two products.
    """

    fab = ['fabric_C-COMPLEMENTOS', 'fabric_J-JEANS', 'fabric_K-CIRCULAR', 'fabric_L-PIEL','fabric_O-POLIPIEL','fabric_P-PLANA','fabric_T-TRICOT']

    product_1_fab = products[products['des_filename'] == product1][fab].values[0]
    product_2_fab = products[products['des_filename'] == product2][fab].values[0]
    product_1_col = products[products['des_filename'] == product1]['cod_color_code'].values[0]
    product_2_col = products[products['des_filename'] == product2]['cod_color_code'].values[0]

    fab = cosine_similarity([product_1_fab], [product_2_fab])
    col = 1 - abs(product_1_col - product_2_col) / (product_1_col + product_2_col)

    return beta * col + (1 - beta) * fab


def global_similarity(img_sim: float, tab_sim: float, alpha: float = 0.5) -> float:
    """
    Returns the global similarity between two images.

    Parameters
    ----------
    img_sim : float
        Image similarity.
    tab_sim : float
        Table similarity.
    alpha : float
        Weight of the image similarity.

    Returns
    -------
    float
        Global similarity between the two images.
    """

    return alpha * img_sim + (1 - alpha) * tab_sim


def get_all_similar(product: str, product_type: str):
    """
    Get all the products of the same type.

    Parameters
    ----------
    product : str
        Name of the product.
    product_type : str
        Type of the product.

    Returns
    -------
    list
        List of all the products of the same type.
    """

    df = products[products['des_product_type'] == product_type]

    all_class = []
    for _, row in df.iterrows():
        all_class.append((row['des_filename'], global_similarity(img_similarity(product, row['des_filename']),
                                                                tab_similarity(product, row['des_filename']), alpha=0.8)))
        
    all_class = sorted(all_class, key=lambda x: x[1], reverse=True)

    return all_class


def get_similar_products(product: str, min_products: int = 5):
    """
    Get similar products of the same type.

    Parameters
    ----------
    product : str
        Name of the product.
    min_products : int
        Minimum number of similar products.

    Returns
    -------
    list
        List of similar products.
    """
    row = products[products['des_filename'] == product]
    p_type = row['des_product_type'].values[0]

    fst_level_products = get_nth_level_products(product, p_type, pst_list)
    
    if len(fst_level_products) < min_products:
        fst_level_products, _ = zip(*get_all_similar(product, p_type))

    sim = []
    for p in fst_level_products:
        sim_product = global_similarity(img_similarity(product, p),
                                        tab_similarity(product, p, beta=0.9), alpha=0.8)
        sim.append((p, sim_product))

    sim = sorted(sim, key=lambda x: x[1], reverse=True)

    return sim


def get_complementary_products(product: str, sim_products: list, desired_type: str, min_products: int = 5):
    """
    Get complementary products of a given type by looking at the similar products of the given product.

    Parameters
    ----------
    product : str
        Name of the product.
    sim_products : list
        List of similar products.
    desired_type : str
        Desired product type.
    min_products : int
        Minimum number of complementary products.

    Returns
    -------
    list
        List of complementary products of the given type.
    """

    complementary_products = []
    for p in sim_products:
        p_pst_list = pst_list[p]['related_products']

        for p2 in p_pst_list:
            p2_type = pst_list[p2]['type']
            if p2_type == desired_type:
                complementary_products.append(p)

    if len(complementary_products) < min_products:
        print(f'Not enough complementary products for {desired_type}. Getting more...')
        
        # row = products[products['des_filename'] == product]
        # p_type = row['des_product_type'].values[0]
        complementary_products, _ = zip(*get_all_similar(product, desired_type))

        # for p in similar_products:
        #     comp = get_nth_level_products(p, desired_type, pst_list)
        #     for p2 in comp:
        #         if p2 not in complementary_products:
        #             complementary_products.append(p2)

    return complementary_products
