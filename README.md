# Herbarium-Label-Generator
This simple python script is a herbarium label generator that enables easy creation of pdf files from .csv or .xlsx tables. I created this because other open projects did not quite have what I wanted for my personal herbarium. If you'd like to have deep integration with iNaturalist this is not for you but other projects are out there!
Example? Here you go:

<img width="1678" height="1187" alt="ExampleLabels" src="https://github.com/user-attachments/assets/77d97b8f-f9a2-4c5a-bf7c-e55a33753a91" />
(darkmode on my pdf viewer just so nobody's eyes will hurt)


Required structure
- Input file: Excel (.xlsx) or CSV (.csv), one row per specimen.
- Requires column names (case-sensitive). It is currently set up as 4 rows each containing 4 columns followed by 2 text blocks each one column.
- The input file path is set where load_data(...) is called in the main block.

Workings
- Loads the data file and replaces missing values with empty strings.
- Creates a landscape A4 PDF with 4 labels per page (2 columns x 2 rows).
- Each label is 14 cm wide and 10 cm high, with a border and inner margins (smaller labels are just too small from my personal expierence).
- At the top of each label there are 4 compact rows, each with 4 fields, printed as “Name: value”.
- Below that are two larger text blocks: “Color Information” and “Description”. The description block is taller so it can hold more text.

Customisation
1) Input and output paths
- Change the input file path in the main block:
  generator.load_data(r"Path2YourFile/Filename.xlsx")
  or if you use a csv adjust to
  generator.load_data(r"Path2YourFile/Filename.csv")
- Change the output PDF path where generate_pdf(...) is called:
  generator.generate_pdf(r"Path2TheOutputFile/Filename.pdf")

2) Label size and layout
- In AdvancedHerbariumConfig.__init__:
  self.label_width  = 14.0   # cm, horizontal size
  self.label_height = 10.0   # cm, vertical size
- For A4 this is a very appropriate size but it could technically be slightly larger
- The script uses landscape A4 and a fixed 2x2 grid in generate_pdf().

3) Fields in the 4 information rows
- In AdvancedHerbariumConfig.__init__, look at self.info_rows.
- Each row is defined as:
  LabelRow([      LabelField("Display Name", "column_name", width_ratio),      ...  ], height=0.75)
- "Display Name" is the text shown on the label (e.g. "Family").
- "column_name" must match a column in your data (e.g. "family").
- width_ratio controls relative width of each field in that row (numbers are scaled to fill the row).

4) Text blocks (Color Information and Description)
- In AdvancedHerbariumConfig.__init__, look at self.text_blocks:
  TextBlock("Color Information", "color_information", height_ratio)
  TextBlock("Description", "description", height_ratio)
- height_ratio controls how much of the remaining vertical space each block gets.
  Example:
    Color Information: height_ratio = 1.0
    Description:       height_ratio = 2.0
  makes Description about twice as tall as Color Information.

5) Fonts and font sizes
- In AdvancedHerbariumConfig.__init__:
  self.default_font      = "Times-Roman"
  self.label_font_size   = 7   # for field names
  self.value_font_size   = 9   # for values
  self.min_font_size     = 5   # minimal size of the font so its still readalbe coming from a regular printer

6) Row height and spacing
- Each LabelRow(..., height=0.75) controls the row height in cm.
- Other spacing parameters:
  self.margin        = 0.4   # inner margin of the label in cm
  self.field_spacing = 0.1   # horizontal space between fields in cm

Things that generally should not be changed
- The internal drawing methods:
  _draw_info_row, _draw_text_block, _draw_label, generate_pdf
  These handle word wrapping, positioning and page layout.
- The meaning of width_ratio in LabelField and height_ratio in TextBlock.
  Keep them as positive numbers; only change their relative values.

Minimum steps to take
1) Point load_data(...) to your own .xlsx or .csv file.
2) Make sure your file has the required column names, or adjust the column_name values in self.info_rows and self.text_blocks.
alternativly if you do not have that many columns just use the first 1, 2, or 3 columns of each row and/or optionally delete some rows entirely
3) Optionally adjust height_ratio for the two text blocks so that the first or second textblock gets more space or delete one entirely if your descriptions are extremly long
4) Optionally rename fields (Display Name) or tweak font sizes and label dimensions.
