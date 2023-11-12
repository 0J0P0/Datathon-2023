import pandas as pd
import streamlit as st
from PIL import Image
from time import sleep
from similarities import get_similar_products, get_complementary_products


def get_aggregations(data, agg_family):
    """
    Get the aggregations of the data.
    
    Parameters
    ----------
    data : pandas.DataFrame
    Dataframe containing the data.

    agg_family : list
    List of aggregated families.
    """

    dic_st = {}
    for t in agg_family:
        dic_st[t] = {}
        fam_prod = list(data[data['des_product_aggregated_family'] == t]['des_product_family'].unique())
        
        for agg_fam in fam_prod:
            dic_st[t][agg_fam] = []
            prod_type = list(data[data['des_product_family'] == agg_fam]['des_product_type'].unique())
            dic_st[t][agg_fam] = prod_type
    return dic_st



def main():
    st.title("Fashion Compatibility Predictor", anchor="center")
    st.header("Datathon 2023 - Mango Challenge")
    st.subheader("Team: Data3")

    # relate each image to a product family
    data = pd.read_csv("products_clean.csv")
    get_product = {row["des_filename"].split("/")[-1]: [row["des_product_aggregated_family"], row["des_product_family"], row["des_product_family"]] for _, row in data.iterrows()}
    agg_family = data['des_product_aggregated_family'].unique()
    prod_family = data['des_product_family'].unique()
    prod_type = data['des_product_type'].unique()
    aggregations = get_aggregations(data, agg_family)

    # ask the image that the user wants to find similar products to
    uploaded_file = st.file_uploader("Choose a product image...", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        product = get_product[uploaded_file.name]
        st.image(image, caption=f"{product[2]}", use_column_width=False)
        outfit = ["datathon/images/"+uploaded_file.name]

        dic_reg = {}

        agg_family_exclude = [x for x in agg_family if x != product[0]]
        dic_reg['agg_family_choosen'+'1'] = st.selectbox("Select the aggregated family product that you would like to add to your outfit", [""] + agg_family_exclude,key="agg_family_0")
        if dic_reg['agg_family_choosen'+'1'] != "":        
            more_cloth = True
            it = 0
            dic_reg['next_cloth0'] = "" 

            # while the user wants to add more clothes to the outfit
            while more_cloth:
                it += 1
                if it > 1:
                    while dic_reg['next_cloth'+str(it-1)] == "":
                        sleep(1)
                    if dic_reg['next_cloth'+str(it-1)] == "Yes":
                        dic_reg['agg_family_choosen'+str(it)] = st.selectbox("Select the aggregated family product that you would like to add to your outfit", [""] + agg_family_exclude,key=f"agg_family_{it}")
                
                # wait for the user to choose the aggregated family for the next piece of clothing
                while dic_reg['agg_family_choosen'+str(it)] == "":
                    sleep(1)
                if dic_reg['agg_family_choosen'+str(it)] != "" and (dic_reg['next_cloth'+str(it-1)] == "Yes" or (it == 1)):
                    dic_reg['prod_family_choosen'+str(it)] = st.selectbox("Select the family product that you would like to add to your outfit", [""] + list(aggregations[dic_reg['agg_family_choosen'+str(it)]].keys()),key=f"prod_family_{it}")
                    
                    # wait for the user to choose the family for the next piece of clothing
                    while dic_reg['prod_family_choosen'+str(it)] == "":
                        sleep(1)
                    if dic_reg['prod_family_choosen'+str(it)] != "":
                        dic_reg['prod_type_choosen'+str(it)] = st.selectbox("Select the type of product that you would like to add to your outfit", [""] + list(aggregations[dic_reg['agg_family_choosen'+str(it)]][dic_reg['prod_family_choosen'+str(it)]]),key=f"prod_type_{it}")
                        
                        # wait for the user to choose the type for the next piece of clothing
                        while dic_reg['prod_type_choosen'+str(it)] == "":
                            sleep(1)
                        if dic_reg['prod_type_choosen'+str(it)] != "":
                            dic_reg['cloth_chosen'+str(it)] = st.selectbox(f"Choose the {dic_reg['prod_type_choosen'+str(it)]} that you would like to add to your outfit", ["", f"{dic_reg['prod_type_choosen'+str(it)]} 1", f"{dic_reg['prod_type_choosen'+str(it)]} 2", f"{dic_reg['prod_type_choosen'+str(it)]} 3", f"{dic_reg['prod_type_choosen'+str(it)]} 4", f"{dic_reg['prod_type_choosen'+str(it)]} 5"],key = f"prod_choosen_{it}")

                            # get the complementary product based on similar products to the last piece of clothing added to the outfit
                            similar_products, _ = zip(*get_similar_products(outfit[-1]))
                            matching_clothes = get_complementary_products(outfit[-1],list(similar_products),dic_reg['prod_type_choosen'+str(it)])
                            matching_clothes = matching_clothes[:5]

                            # show the user the 5 best complementary products to the last piece of clothing added to the outfit
                            columns = st.columns(5)
                            for i, col in enumerate(columns):
                                col.image(matching_clothes[i], use_column_width=True, caption=f"{dic_reg['prod_type_choosen'+str(it)]} {i+1}")
                            
                            # wait until the user chooses the next piece of clothing
                            while dic_reg['cloth_chosen'+str(it)] == "":
                                sleep(1)
                            if dic_reg['cloth_chosen'+str(it)] != "":
                                outfit.append(matching_clothes[int(dic_reg['cloth_chosen'+str(it)].split()[-1])-1])
                                st.write("You have chosen the following outfit:")
                                columns = st.columns(len(outfit))
                                for i, col in enumerate(columns):
                                    col.image(outfit[i], use_column_width=True, caption=f"{get_product[outfit[i].replace('datathon/images/', '', 1)][2]}")

                                # ask the user if he wants to add more clothes to the outfit
                                dic_reg['next_cloth'+str(it)] = st.selectbox("Do you want to choose another piece of clothing?", ["", "Yes", "No"],key = f"next_cloth_{it}")
                                while dic_reg['next_cloth'+str(it)] == "":
                                    sleep(1)
                                if dic_reg['next_cloth'+str(it)] == "No":
                                    st.write("Thank you for using our app!")
                                    more_cloth = False
                                elif dic_reg['next_cloth'+str(it)] == "Yes":
                                    more_cloth = True



if __name__ == "__main__":
    main()

