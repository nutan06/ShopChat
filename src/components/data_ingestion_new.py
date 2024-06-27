import os
import sys
from src.exception import CustomException
from src.logger import logging
import gzip
import pandas as pd
import s3fs
from dataclasses import dataclass

@dataclass
class DataIngestionConfig:
    
    file_name_pref              = ['0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f']
    image_meta_data_path:   str = "s3://amazon-berkeley-objects/images/metadata/images.csv.gz"
    listing_meta_data_path: str = "s3://amazon-berkeley-objects/listings/metadata/"
    save_json_path:         str = os.path.join('artifacts', 'dataset.json')

class DataIngestion:
    def __init__(self):
        self.ingestion_config=DataIngestionConfig()
    
    def initiate_data_ingestion(self):
        logging.info("Data Ingestion - started")
        try:
            logging.info("Data Ingestion - file loading from AWS s3 server - started")
            
            listing = []
            for prefix in DataIngestionConfig.file_name_pref:
                data = pd.read_json(f"{DataIngestionConfig.listing_meta_data_path}listings_{prefix}.json.gz", lines=True)
                listing.append(data)
           
            listing_meta = pd.concat(listing, ignore_index=True)

            logging.info("Data Ingestion - file loading from AWS s3 server - completed")

            def func_in_en_us_(x):
                if isinstance(x, list):  # Check if x is a list before iterating
                    us_texts = [item["value"] for item in x if item["language_tag"] == "en_US"]
                    return us_texts[0] if us_texts else None
                else:
                    return None  # Handle cases where x is not a list (e.g., a float)

            logging.info("Data Ingestion - processing listing meta data - started")

            listing_meta = listing_meta.assign(brand_in_en_us=listing_meta.brand.apply(func_in_en_us_))
            listing_meta = listing_meta.assign(bullet_point_in_en_us=listing_meta.bullet_point.apply(func_in_en_us_))
            listing_meta = listing_meta.assign(color_in_en_us=listing_meta.color.apply(func_in_en_us_))
            listing_meta = listing_meta.assign(fabric_type_in_en_us=listing_meta.fabric_type.apply(func_in_en_us_))
            listing_meta = listing_meta.assign(finish_type_in_en_us=listing_meta.finish_type.apply(func_in_en_us_))
            listing_meta = listing_meta.assign(item_keywords_in_en_us=listing_meta.item_keywords.apply(func_in_en_us_))
            listing_meta = listing_meta.assign(item_name_in_en_us=listing_meta.item_name.apply(func_in_en_us_))
            listing_meta = listing_meta.assign(item_shape_in_en_us=listing_meta.item_shape.apply(func_in_en_us_))
            listing_meta = listing_meta.assign(material_in_en_us=listing_meta.material.apply(func_in_en_us_))
            listing_meta = listing_meta.assign(model_name_in_en_us=listing_meta.model_name.apply(func_in_en_us_))
            listing_meta = listing_meta.assign(pattern_in_en_us=listing_meta.pattern.apply(func_in_en_us_))
            listing_meta = listing_meta.assign(product_description_in_en_us=listing_meta.product_description.apply(func_in_en_us_)) 
               
            listing_meta = listing_meta[~listing_meta.item_name_in_en_us.isna()]
            
            logging.info("Data Ingestion - processing listing meta data - completed")

            print(f" number products with US English title: {len(listing_meta)}")

            logging.info("Data Ingestion - processing image meta data - started")

            image_meta = pd.read_csv(DataIngestionConfig.image_meta_data_path)
            
            dataset = listing_meta.merge(image_meta, left_on="main_image_id", right_on="image_id")

            dataset = dataset.drop_duplicates(subset=['item_id'], keep='first')

            def func_image_path_(image_ids):
                if isinstance(image_ids, list):
                    image_paths = [image_meta[image_meta["image_id"] == image_id]["path"].to_list()[0] for image_id in image_ids]
                    return image_paths if image_paths else None
                else:
                    return None
            
            dataset = dataset.assign(other_image_id_path=dataset.other_image_id.apply(func_image_path_))

            logging.info("Data Ingestion - processing image meta data - completed")

            dataset = dataset.drop(columns=['brand', 'bullet_point', 'color', 'fabric_type', 'finish_type', 'item_keywords', 
                                            'item_name', 'item_shape', 'material', 'model_name', 'model_number', 'pattern', 
                                            'product_description', 'style', 'node', 'model_year', 'item_dimensions', 'item_weight',
                                            'image_id', 'main_image_id', 'other_image_id'])

            print(f" number of matching products with US English title and image: {dataset.shape[0]}")

            dataset.to_json(self.ingestion_config.save_json_path, orient='records')

            logging.info("Data Ingestion - completed")
            
            return self.ingestion_config.save_json_path                
            
        except Exception as e:
            raise CustomException(e, sys)

if __name__=="__main__":
    obj=DataIngestion()
    json_file = obj.initiate_data_ingestion()