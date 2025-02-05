# pip install openpyxl pandas
import pandas as pd

def write_to_excel(data, output_path):
    df = pd.DataFrame(data)
    
    # Write to Excel
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)

data = {
 	'task 1': ['2025/02/01', '2025/02/02'],
   	'task 2': [25, 30]
}

write_to_excel(data, './hello.xlsx')