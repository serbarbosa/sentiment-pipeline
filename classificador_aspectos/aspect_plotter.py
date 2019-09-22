import pygal

class Aspect_plotter() :

    def __init__(self, json_data):

        self.json_data = json_data
        self.plotter_data = {}
        process_data()


    def process_data(self):

        #itera por cada aspecto 
        for cell in self.json_data:

            #processa o aspecto somente se a polaridade foi classificada
            if cell['polaridade'] is not '' :
                #insere cada novo aspecto com contagem 0
                if cell['aspecto'] not in self.plotter_data:
                    self.plotter_data[cell['aspecto']] = [0,0]

                #cada aspecto armazena contagem de positivos e de negativos : [pos, neg]
                if cell['polaridade'] is '+' :
                    self.plotter_data[cell['aspecto']][0] += 1
                else:
                    self.plotter_data[cell['aspecto']][0] -= 1
        print(self.plotter_data)










