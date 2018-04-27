from pyslides.presentation import Presentation as P

P = P(biblio_file='biblio.bib')



P.add_slide(model = 'title', title = 'An example of presentation with PySlides',\
                             author      = 'Francesco Rossi',\
                             affiliation = 'Free University')



P.add_slide(model='one_figure',\
            figure = 'cat.jpeg',\
            title='Example')

P.add_citation('einstein1935can')


P.add_slide()
P.add_bullets(y = 0.5,\
              text = [r'''Cats are cute''',r'''Especially this one'''])

P.add_text(x = 0.5,\
           y = 0.1,\
           color='red',\
           text = 'Example of adding text')

P.add_figure(x=0.7,y=0.5,L=0.3,filename='cat.jpeg')



P.render(show_pdf=True)






