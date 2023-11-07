import argparse
import pandas as pd
from fpdf import FPDF

def create_mailing_address(input_file, output_file, owner1_col, owner2_col, addr1_col, addr2_col, city_col, state_col, zip_col):
    df = pd.read_csv(input_file, sep=',')  # Use ',' as the separator
    df.columns = df.columns.str.strip()  # Strip leading and trailing spaces

    # Convert all the fields to strings
    for col in [owner1_col, owner2_col, addr1_col, addr2_col, city_col, state_col, zip_col]:
        df[col] = df[col].astype(str)

    # Replace 'nan' with an empty string
    df.replace('nan', '', inplace=True)

    # Sort the DataFrame by the OWNER1 column
    df.sort_values(by=[owner1_col], inplace=False)

    # Create the mailing address
    df['mailing_address'] = df.apply(lambda row: '\n'.join(filter(None, [row[owner1_col], row[owner2_col], ', '.join(filter(None, [row[addr1_col], row[addr2_col]])), ', '.join([row[city_col], row[state_col], row[zip_col]])])), axis=1)

    pdf = FPDF('L', 'mm', (215.9, 279.4))  # Create a PDF in landscape orientation on letter size paper

    # Dimensions of the text box in mm
    box_height = 28.575
    box_width = 114.3

    # Set the margins to 1 inch (approximately 25.4 mm) at the top and bottom and 0.5 inch (approximately 12.7 mm) at the left
    pdf.set_top_margin(12.7)
    pdf.set_left_margin(25.4)
    pdf.set_right_margin(0.0)

    # Calculate the number of text boxes that can fit on a page
    boxes_per_page_vertically = int((pdf.h - 2 * 12.7) / box_height)
    boxes_per_page_horizontally = int((pdf.w - 0.0 - 25.4) / box_width)

    pdf.add_page()
    
    for index, row in df.iterrows():
        # Check if we need to add a new page
        if index != 0 and index % (boxes_per_page_vertically * boxes_per_page_horizontally) == 0:
            pdf.add_page()

        # Calculate the position of the current text box
        x = 25.4 + (index % boxes_per_page_horizontally) * box_width
        y = 25.4 + ((index % (boxes_per_page_vertically * boxes_per_page_horizontally)) // boxes_per_page_horizontally) * box_height

        pdf.set_xy(x, y)
        pdf.set_font("Times", size = 12)
        pdf.multi_cell(box_width, box_height / 5, txt = row['mailing_address'], align='L')

    pdf.output(output_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create mailing addresses from a CSV file.')
    parser.add_argument('input_file', type=str, help='Input CSV file name')
    parser.add_argument('output_file', type=str, help='Output PDF file name')
    parser.add_argument('--owner1', type=str, default='OWNER1', help='Name of the owner1 column')
    parser.add_argument('--owner2', type=str, default='OWNER2', help='Name of the owner2 column')
    parser.add_argument('--addr1', type=str, default='ADDRGL1', help='Name of the address1 column')
    parser.add_argument('--addr2', type=str, default='ADDRGL2', help='Name of the address2 column')
    parser.add_argument('--city', type=str, default='CITYGL', help='Name of the city column')
    parser.add_argument('--state', type=str, default='STGL', help='Name of the state column')
    parser.add_argument('--zip', type=str, default='ZIPGL', help='Name of the zip code column')

    args = parser.parse_args()

    create_mailing_address(args.input_file, args.output_file, args.owner1, args.owner2, args.addr1, args.addr2, args.city, args.state, args.zip)
