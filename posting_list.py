import os
import pandas as pd


repository = 'Datathon-2023/'
image_path = repository + 'datathon/images/'

products = pd.read_csv(repository + 'products_clean.csv')
outfits = pd.read_csv(repository + 'datathon/dataset/outfit_data.csv')


def get_pst_list(outfit_data: pd.DataFrame, product_data: pd.DataFrame):
    """
    Returns a dictionary containing the product_id, related product_ids (products from same outfit) and features.

    Parameters
    ----------
    outfit_data : pandas.DataFrame
        Dataframe containing the outfit data.
    product_data : pandas.DataFrame
        Dataframe containing the product data.

    Returns
    -------
    dict
        Dictionary containing the product_id, related product_ids and type.
    """

    # if product_pst_list.csv exists, load it and return it
    if os.path.exists(repository + 'product_pst_list.csv'):
        df = pd.read_csv(repository + 'product_pst_list.csv')
        product_pst_list = {}
        for _, row in df.iterrows():
            product_id = row['productid']
            related_products = eval(row['related_products'])  # If the data is in string format
            row_type = str(row['type']) # If the data is in string format

            product_pst_list[product_id] = {'related_products': related_products, 'type': row_type}
        return product_pst_list

    product_pst_list = dict()

    merged_data = pd.merge(outfit_data, product_data, on='cod_modelo_color', how='inner')

    for _, row in merged_data.iterrows():
        product_id = row['des_filename']
        outfit_id = row['cod_outfit']

        if product_id not in product_pst_list:
            product_pst_list[product_id] = {'related_products': [], 'type': str()}

        related_products = merged_data[merged_data['cod_outfit'] == outfit_id]['des_filename'].tolist()
        for p in related_products:
            if p not in product_pst_list[product_id]['related_products']:
                product_pst_list[product_id]['related_products'].append(p)
        
        row_type = row['des_product_type']
        product_pst_list[product_id]['type'] = str(row_type)

    product_ids = []
    related_products_list = []
    type_list = []

    # Extract data from the dictionary
    for product_id, data in product_pst_list.items():
        product_ids.append(product_id)
        related_products_list.append(data['related_products'])
        type_list.append(data['type'])

    # Create a DataFrame
    df = pd.DataFrame({
        'productid': product_ids,
        'related_products': related_products_list,
        'type': type_list
    })

    # Save the DataFrame to a file
    df.to_csv(repository + 'product_pst_list.csv')
    return product_pst_list