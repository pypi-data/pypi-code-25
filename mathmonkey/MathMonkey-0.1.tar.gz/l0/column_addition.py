from pylatex import Document, Section, Subsection, Tabular, MultiColumn, LongTabu, Command
from pylatex import Math
from pylatex.basic import SmallText
from pylatex.position import FlushRight
from pylatex.utils import italic, bold
from random import randint

out_dir = "generated/"

pge_geom = {"tmargin" : "1cm",  "bmargin" : "1cm",  "lmargin" : "1cm",  "rmargin" : "1cm" }

#
# generate a single example string of columnar addition for numbers of n digits
#
def gen_example(n_digits, n_nums):
    min, max = pow(10, n_digits - 1), pow(10, n_digits)
    assert(min * 10 == max)

    tab = Tabular(' c c ', row_height=1.2)
    for n in range(0, n_nums):
        rnum = randint(min, max)
        if (n == 0) :
            tab.add_row(("", rnum))
        else:
            tab.add_row(("+", rnum))    
    tab.add_hline()
    tab.add_empty_row()
    tab.add_empty_row()
    return tab

#
# main generator funcion
#
def gen(f_nm, n_ex, n_cols):
    print("----- START -----")

    doc = Document(geometry_options = pge_geom, lmodern=True)

    with doc.create(Section('The simple stuff', numbering=False)):
        doc.append('Some regular text and some')
        doc.append(italic('italic text. '))
        doc.append('\nAlso some crazy characters: $&#{}')

    doc.append(Command('fontsize', arguments = ['11', '14']))
    doc.append(Command('fontfamily', arguments = ['pcr']))
    doc.append(Command('hfill'))
    doc.append(Command('raggedright'))
    doc.append(Command('selectfont'))
    doc.append(FlushRight())
               
    # Add statement table
    with doc.create(LongTabu("X[r] " * n_cols,  row_height=2.0)) as data_table:
        for i in range(30):
            row = ['  ' + str(n + i*n_cols) + '.' for n in range(0, n_cols)]
            data_table.add_row(row, mapper=bold, color="lightgray")

            row = [gen_example(10, 3) for n in range(0, n_cols)]
            data_table.add_row(row)

    # write the file
    doc.generate_pdf(out_dir + '/' + f_nm, clean_tex=False)
    print("----- DONE -----")

if __name__ == '__main__' :
    # ik:>> TODO :>> do a check for out_dir
    gen('test', 100, 5)
    #for i in range(1, 10):
    #    for j in range(2, 5):
    #        print(gen_example(i, j))
