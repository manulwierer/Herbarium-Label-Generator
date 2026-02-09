import pandas as pd
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm, mm
from reportlab.pdfgen import canvas
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase.pdfmetrics import stringWidth
from typing import List, Dict, Tuple, Optional

class LabelField:
    
    def __init__(self, name: str, column: str, width_ratio: float = 1.0):

        self.name = name
        self.column = column
        self.width_ratio = width_ratio

class LabelRow:
    
    def __init__(self, fields: List[LabelField], height: float = 0.75):

        self.fields = fields
        self.height = height
    
    def get_column_names(self) -> List[str]:
        return [f.column for f in self.fields]

class TextBlock:
    
    def __init__(self, name: str, column: str, height_ratio: float = 1.0):

        self.name = name
        self.column = column
        self.height_ratio = height_ratio

class AdvancedHerbariumConfig:
    
    def __init__(self):
        # Label dimensions (in cm) - 4 labels per A4 page
        self.label_width = 14.0  # Long side
        self.label_height = 10.0  # Short side
        
        # Font settings
        self.default_font = "Times-Roman"
        self.label_font_size = 7  # For field labels
        self.value_font_size = 9  # For column values
        self.min_font_size = 5    # Ensures readability for standard printers
        
        # Spacing (in cm)
        self.margin = 0.4
        self.field_spacing = 0.1  # Space between fields horizontally
        
        # the 4 rows
        self.info_rows = [
            LabelRow([
                LabelField("Family", "family", 0.25),
                LabelField("Genera", "genera", 0.25),
                LabelField("Species", "species", 0.25),
                LabelField("Subspecies", "subspecies", 0.25),
            ], height=0.75),
            
            LabelRow([
                LabelField("ID", "id", 0.25),
                LabelField("Date", "date", 0.25),
                LabelField("Elevation", "elevation", 0.25),
                LabelField("Reference", "reference", 0.25),
            ], height=0.75),
            
            LabelRow([
                LabelField("DD-Latitude", "dd-latitude", 0.25),
                LabelField("DD-Longitude", "dd-longitude", 0.25),
                LabelField("Anthesis", "anthesis", 0.25),
                LabelField("Fruit/Seed", "fruit/seed", 0.25),
            ], height=0.75),
            
            LabelRow([
                LabelField("Complete Specimen", "complete specimen", 0.25),
                LabelField("Coverage Species", "coverage species", 0.25),
                LabelField("Coverage Vegetation", "coverage vegetation", 0.25),
                LabelField("Variant", "variant", 0.25),
            ], height=0.75),
        ]
        
        # the 2 text blocks
        self.text_blocks = [
            TextBlock("Color Information", "color_information", 0.8),
            TextBlock("Description", "description", 2.2),
        ]

class AdvancedHerbariumLabelGenerator:
    
    def __init__(self, config: AdvancedHerbariumConfig = None, data_file: Optional[str] = None):
        self.config = config or AdvancedHerbariumConfig()
        self.data = None
        
        if data_file:
            self.load_data(data_file)
    
    def load_data(self, file_path: str):
        try:
            if file_path.endswith('.xlsx'):
                self.data = pd.read_excel(file_path)
            else:
                self.data = pd.read_csv(file_path)
            
            self.data = self.data.fillna("")
            
            print(f"✓ Loaded {len(self.data)} specimens")
            print(f"✓ Columns: {', '.join(self.data.columns.tolist())}")
            
            all_fields = set()
            for row in self.config.info_rows:
                all_fields.update(row.get_column_names())
            for block in self.config.text_blocks:
                all_fields.add(block.column)
            
            missing = all_fields - set(self.data.columns)
            if missing:
                print(f"⚠ Warning: Missing columns: {missing}")
        
        except Exception as e:
            raise Exception(f"Error loading file: {e}")
    
    def _get_text_width(self, text: str, font_name: str, font_size: int) -> float:
        return stringWidth(text, font_name, font_size)
    
    def _wrap_text(self, text: str, max_width: float, font_name: str, font_size: int) -> List[str]:
        if not text:
            return [""]
        
        text = str(text)
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = (current_line + " " + word).strip()
            if self._get_text_width(test_line, font_name, font_size) <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines if lines else [""]
    
    def _draw_info_row(self, c: canvas.Canvas, row: LabelRow, data: Dict, 
                       x: float, y: float, width: float):
        available_width = width - self.config.field_spacing * cm * (len(row.fields) - 1)
        total_ratio = sum(f.width_ratio for f in row.fields)
        
        current_x = x
        
        for i, field in enumerate(row.fields):
            field_width = (available_width * field.width_ratio / total_ratio)
            
            # Get value
            value = str(data.get(field.column, ""))
            if value and value != "nan":
                # Draw field name (small, can wrap)
                label_font_size = self.config.label_font_size
                label_lines = self._wrap_text(field.name, field_width, 
                                             self.config.default_font, label_font_size)
                
                label_height = len(label_lines) * label_font_size * 1.1
                
                label_y = y + row.height * cm - label_height - 2
                c.setFont(self.config.default_font, label_font_size)
                c.setFillColor(colors.black)
                
                for line in label_lines:
                    c.drawString(current_x, label_y, line + ":")
                    label_y -= label_font_size * 1.1
                
                c.setFont(self.config.default_font, self.config.value_font_size)
                value_lines = self._wrap_text(value, field_width, 
                                             self.config.default_font, 
                                             self.config.value_font_size)
                
                value_y = y + 2
                for line in value_lines[:2]:  # Limit to 2 lines for values
                    c.drawString(current_x, value_y, line)
                    value_y += self.config.value_font_size * 1.1
            
            current_x += field_width + self.config.field_spacing * cm
    
    def _draw_text_block(self, c: canvas.Canvas, block: TextBlock, data: Dict,
                        x: float, y: float, width: float, height: float):
        c.setFont(f"{self.config.default_font.split('-')[0]}-Bold", 
                 self.config.value_font_size)
        c.setFillColor(colors.black)
        c.drawString(x, y + height - self.config.value_font_size - 2, 
                    f"{block.name}:")
        
        value = str(data.get(block.column, ""))
        if value and value != "nan":
            c.setFont(self.config.default_font, self.config.value_font_size)
            
            content_y = y + height - self.config.value_font_size * 2.5
            lines = self._wrap_text(value, width - 4, 
                                   self.config.default_font, 
                                   self.config.value_font_size)
            
            for line in lines:
                if content_y < y + 2:
                    break
                c.drawString(x + 2, content_y, line)
                content_y -= self.config.value_font_size * 1.2
    
    def _draw_label(self, c: canvas.Canvas, data: Dict, x: float, y: float):
        label_width = self.config.label_width * cm
        label_height = self.config.label_height * cm
        
        c.setLineWidth(0.5)
        c.rect(x, y, label_width, label_height)
        
        inner_width = label_width - 2 * self.config.margin * cm
        current_y = y + label_height - self.config.margin * cm
        
        for row in self.config.info_rows:
            current_y -= row.height * cm
            self._draw_info_row(c, row, data, 
                               x + self.config.margin * cm, 
                               current_y, inner_width)
        
        remaining_height = current_y - y - self.config.margin * cm
        total_ratio = sum(b.height_ratio for b in self.config.text_blocks)
        
        for block in self.config.text_blocks:
            block_height = remaining_height * block.height_ratio / total_ratio
            current_y -= block_height
            
            self._draw_text_block(c, block, data,
                                 x + self.config.margin * cm,
                                 current_y, inner_width, block_height)
    
    def generate_pdf(self, output_file: str = "herbarium_labels.pdf"):
        if self.data is None:
            raise ValueError("No data loaded. Use load_data() first.")
        
        pagesize = landscape(A4)
        c = canvas.Canvas(output_file, pagesize=pagesize)
        
        page_width, page_height = pagesize
        
        label_width = self.config.label_width * cm
        label_height = self.config.label_height * cm
        
        cols = 2
        rows = 2
        
        h_gap = (page_width - cols * label_width) / (cols + 1)
        v_gap = (page_height - rows * label_height) / (rows + 1)
        
        if h_gap < 0 or v_gap < 0:
            raise ValueError(
                f"Labels do not fit on page! h_gap={h_gap:.2f}pt, v_gap={v_gap:.2f}pt. "
                f"Reduce label size or check page orientation."
            )
        
        labels_per_page = cols * rows
        label_count = 0
        
        for idx, (_, row_data) in enumerate(self.data.iterrows()):
            if label_count > 0 and label_count % labels_per_page == 0:
                c.showPage()
            
            pos = label_count % labels_per_page
            col = pos % cols  # 0 or 1
            row = pos // cols  # 0 or 1 (0 = top row)
            
            label_x = h_gap + col * (label_width + h_gap)
            label_y = v_gap + (rows - 1 - row) * (label_height + v_gap)
            
            try:
                self._draw_label(c, row_data.to_dict(), label_x, label_y)
            except Exception as e:
                print(f" Error drawing label {idx + 1}: {e}")
                # Draw error indicator
                c.setFont("Helvetica", 8)
                c.setFillColor(colors.red)
                c.rect(label_x, label_y, label_width, label_height, 
                      fill=False, stroke=True)
                c.drawString(label_x + 5, label_y + label_height - 15, 
                           f"Error: {str(e)[:50]}")
            
            label_count += 1
        
        c.save()
        print(f"✓ PDF generated: {output_file}")
        print(f"✓ Total labels: {label_count}")
        print(f"✓ Pages: {(label_count - 1) // labels_per_page + 1}")
        print(f"✓ Layout: {cols} columns × {rows} rows per page (landscape A4)")
        print(f"✓ Gaps: horizontal={h_gap/cm:.2f}cm, vertical={v_gap/cm:.2f}cm")

if __name__ == "__main__":
    print("=" * 70)
    print("HERBARIUM SPECIMEN LABEL GENERATOR")
    print("=" * 70)
    
    config = AdvancedHerbariumConfig()

    generator = AdvancedHerbariumLabelGenerator(config)
    
    # Load your data and generate PDF
    print("\nLoading data...")
    generator.load_data(r"YourInputFilePathHere.csv/xlsx")
    
    print("\nGenerating PDF...")
    generator.generate_pdf(r"/YourOutputFilePathHere.pdf")
    
    print("\n✓ Done! Check for herbarium_labels.pdf in the current directory")

