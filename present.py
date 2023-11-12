import pandas as pd
import streamlit as st
from PIL import Image
from time import sleep

def get_aggregations(data, agg_family):
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

    # relate each image to a product family
    data = pd.read_csv("products_clean.csv")
    get_product = {row["des_filename"].split("/")[-1]: [row["des_product_aggregated_family"], row["des_product_family"], row["des_product_family"]] for _, row in data.iterrows()}
    agg_family = data['des_product_aggregated_family'].unique()
    prod_family = data['des_product_family'].unique()
    prod_type = data['des_product_type'].unique()
    aggregations = get_aggregations(data, agg_family)

    # st.write("Upload an image of a product to see how compatible it is with other products.")

    uploaded_file = st.file_uploader("Choose a product image...", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        product = get_product[uploaded_file.name]
        st.image(image, caption=f"{product}", use_column_width=False)
        outfit = ["datathon/images/"+uploaded_file.name]

        dic_reg = {}

        agg_family_exclude = [x for x in agg_family if x != product[0]]
        dic_reg['agg_family_choosen'+'1'] = st.selectbox("Select the aggregated family product that you would like to add to your outfit", [""] + agg_family_exclude,key="agg_family_0")
        if dic_reg['agg_family_choosen'+'1'] != "":        
            more_cloth = True
            it = 0
            dic_reg['next_cloth0'] = "" 

            while more_cloth:
                it += 1
                print(it)
                print(dic_reg)
                if it > 1:
                    while dic_reg['next_cloth'+str(it-1)] == "":
                        sleep(1)
                    if dic_reg['next_cloth'+str(it-1)] == "Yes":
                        dic_reg['agg_family_choosen'+str(it)] = st.selectbox("Select the aggregated family product that you would like to add to your outfit", [""] + agg_family_exclude,key=f"agg_family_{it}")
                while dic_reg['agg_family_choosen'+str(it)] == "":
                    sleep(1)
                if dic_reg['agg_family_choosen'+str(it)] != "" and (dic_reg['next_cloth'+str(it-1)] == "Yes" or (it == 1)):
                    #dic_reg['prod_family_choosen'+str(it)] = ""
                    dic_reg['prod_family_choosen'+str(it)] = st.selectbox("Select the family product that you would like to add to your outfit", [""] + list(aggregations[dic_reg['agg_family_choosen'+str(it)]].keys()),key=f"prod_family_{it}")
                    while dic_reg['prod_family_choosen'+str(it)] == "":
                        sleep(1)
                    if dic_reg['prod_family_choosen'+str(it)] != "":
                        dic_reg['prod_type_choosen'+str(it)] = st.selectbox("Select the type of product that you would like to add to your outfit", [""] + list(aggregations[dic_reg['agg_family_choosen'+str(it)]][dic_reg['prod_family_choosen'+str(it)]]),key=f"prod_type_{it}")
                        while dic_reg['prod_type_choosen'+str(it)] == "":
                            sleep(1)
                        if dic_reg['prod_type_choosen'+str(it)] != "":
                            dic_reg['cloth_chosen'+str(it)] = st.selectbox(f"Choose the {dic_reg['prod_type_choosen'+str(it)]} that you would like to add to your outfit", ["", f"{dic_reg['prod_type_choosen'+str(it)]} 1", f"{dic_reg['prod_type_choosen'+str(it)]} 2", f"{dic_reg['prod_type_choosen'+str(it)]} 3", f"{dic_reg['prod_type_choosen'+str(it)]} 4", f"{dic_reg['prod_type_choosen'+str(it)]} 5"],key = f"prod_choosen_{it}")

                            matching_clothes = ["datathon/images/2019_41085800_02.jpg", "datathon/images/2019_41085800_02.jpg", "datathon/images/2019_41085800_02.jpg", "datathon/images/2019_41085800_02.jpg", "datathon/images/2019_41085800_02.jpg"]
                        # similar_products, _ = zip(*get_similar_products(outfit[-1]))
                        # matching_clothes = get_complementary_products(similar_products, cloth_chosen)
                            matching_clothes = matching_clothes[:5]

                            columns = st.columns(5)
                            for i, col in enumerate(columns):
                                col.image(matching_clothes[i], use_column_width=True, caption=f"{dic_reg['prod_type_choosen'+str(it)]} {i+1}")
                            while dic_reg['cloth_chosen'+str(it)] == "":
                                sleep(1)
                            if dic_reg['cloth_chosen'+str(it)] != "":
                                outfit.append(matching_clothes[int(dic_reg['cloth_chosen'+str(it)].split()[-1])-1])
                                st.write("You have chosen the following outfit:")
                                columns = st.columns(len(outfit))
                                for i, col in enumerate(columns):
                                    col.image(outfit[i], use_column_width=True, caption=f"{get_product[outfit[i].replace('datathon/images/', '', 1)][2]}")

                                #producte agafat
                                
                                #product = get_product[outfit[-1].replace('datathon/images/', '', 1)]
                                #agg_family_exclude = [x for x in agg_family_exclude if x != product]
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






















