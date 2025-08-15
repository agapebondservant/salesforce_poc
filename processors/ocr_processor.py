import glob
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    PdfPipelineOptions,
)
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.models.ocr_mac_model import OcrMacOptions
import os
import shutil
import pandas
import data_collection_processor
from data_collection_processor import DataCollectionProcessor
import importlib
importlib.reload(data_collection_processor)

class OcrProcessor:
    def __init__(self, **kwargs):
        """
        Initialize the DocumentConverter.
        """
        self.doc_converter = self._initialize_converter(**kwargs)

    def _initialize_converter(self):
        """Set up the appropriate DocumentConverter based on the mode."""
        return DocumentConverter()

    def extract_tables(self, input_file: str) -> str:
         conv_result = self.doc_converter.convert(input_file)
        
         return [table.export_to_dataframe().to_markdown() for table in conv_result.document.tables]

    def process(self, input_dir: str, output_dir: str, review_dir: str) -> None:
        """
        Convert all PDFs in the input directory to Markdown and save them to the output directory.

        Args:
            input_dir (str): Directory containing PDF files
            output_dir (str): Directory for converted Markdown files
            review_dirs (list): Directories containing outputted files that should be reviewed - currently includes "tables"
        """
        input_pdfs = glob.glob(f"{input_dir}/*.pdf")

        if not input_pdfs:
            print(f"No PDFs found in {input_dir}.")
            return
        
        os.makedirs(output_dir, exist_ok=True)

        for i in input_pdfs:
            conv_result = self.doc_converter.convert(i)
            filepath = f"{output_dir}/{conv_result.input.file.stem}.md"
            
            with open(filepath, "w") as f:
                print(f"Writing file: {f.name}...")
                f.write(conv_result.document.export_to_markdown())
                
                if len(review_dir) and len(conv_result.document.tables):
                    os.makedirs(review_dir, exist_ok=True)
                    print(f"Copying file to tables directory: {os.path.basename(filepath)}...")
                    shutil.copy(f.name, review_dir)
        print("Conversion to markdown completed.")
                            
if __name__ == "__main__":              
    processor = OcrProcessor()
    data_collector = DataCollectionProcessor()
    
    try:

        input_dirs, output_dirs, review_dirs = data_collector.process(
            f"{Path(__file__).resolve().parents[1]}/resources", 
            f"{Path(__file__).resolve().parents[1]}/scraped",
            f"{Path(__file__).resolve().parents[1]}/tables")

        for input_dir, output_dir, review_dir in zip(input_dirs, output_dirs, review_dirs):
            processor.process(input_dir, output_dir, review_dir)
        
    except Exception as e:
        
        print("An exception occurred:")
        traceback.print_exc()
        print(f"Exception message: {e}")
