#import pygal
#from pygal.style import Style
#from pygal import Config
import json

class Aspect_plotter() :

    def __init__(self, json_data):

        self.json_data = json_data
        self.plotter_data = {}
        self.process_data()


    def process_data(self):

        #itera por cada aspecto 
        for cell in self.json_data:

            #processa o aspecto somente se a polaridade foi classificada
            if cell["polaridade"] != '' :
                #insere cada novo aspecto com contagem 0
                if cell["aspecto"] not in self.plotter_data:
                    self.plotter_data[cell["aspecto"]] = [0,0]

                #cada aspecto armazena contagem de positivos e de negativos : [pos, neg]
                if cell["polaridade"] == '+' :
                    self.plotter_data[cell["aspecto"]][0] += 1
                elif cell["polaridade"] == '-':
                    self.plotter_data[cell["aspecto"]][1] -= 1
        
        self.plotter_data = sorted(self.plotter_data.items(), key = lambda kv: kv[1][0]+abs(kv[1][1]), reverse = True)
        self.plotter_data = json.dumps(self.plotter_data)
        print(self.plotter_data)
    
    """
    def plot_by_aspect(self, style='pie'):

        #ordenando itens por relevancia
        sorted_data = sorted(self.plotter_data.items(), key = lambda kv: kv[1][0]+abs(kv[1][1]), reverse = True)
        
        if len(sorted_data) < 10: max_length = len(sorted_data)
        
        # --- Pie ----
        if style == 'pie':

            gauge = pygal.SolidGauge(inner_radius = 0.70)
            
            max_length = 10
            if len(sorted_data) < max_length: max_length = len(sorted_data)
            for item in sorted_data[:max_length]:
                gauge.add(item[0], [{'value' : item[1][0], 'max_value' : item[1][0] + abs(item[1][1])}])

            #gauge.render_in_browser()
            #result_chart = gauge.render_data_uri()
            result_chart = gauge.render()
            #result_chart = gauge.render_to_file('processed_data/gauge.svg')

        # --- Bar ----
        elif(style == 'bars'):
            config = Config()
            config.human_readable = True
            config.print_labels = True
            #config.legend_at_bottom = True
            config.show_legend = False
            custom_style = Style(
                    font_family='googlefont:Raleway',
                    colors=('CornflowerBlue', 'IndianRed')
                    )

            max_length = 15
            if len(sorted_data) < max_length: max_length = len(sorted_data)
            
            bar_plotter = pygal.StackedBar(config, style=custom_style)
            bar_plotter.x_labels = map(str, (sorted_data[i][0] for i in range(max_length)))
            
            bar_plotter.add("+", [sorted_data[i][1][0] for i in range(max_length)], rounded_bars=20)
            bar_plotter.add("-", [sorted_data[i][1][1] for i in range(max_length)], rounded_bars=20)
            '''
            for i in range(max_length):
                bar_plotter.add(sorted_data[i][0] + " +", [None for j in range(i)] + [sorted_data[i][1][0]]
                                    + [None for k in range(max_length - i -1)])
                bar_plotter.add(sorted_data[i][0] + " -", [None for j in range(i)] + [sorted_data[i][1][1]]
                                    + [None for k in range(max_length - i -1)])
            ''' 
            #bar_plotter.render_in_browser()
            #bar_plotter.render_to_file('processed_data/bar.svg')
            result_chart = bar_plotter.render()
        
        # --- Treemap ----
        elif(style == 'treemap'):
            treemap_plotter = pygal.Treemap()
            
            max_length = 20
            if len(sorted_data) < max_length: max_length = len(sorted_data)
            i = 0

            for item in sorted_data[:max_length]:
                treemap_plotter.add(item[0], [{'value':item[1][0], 'label' : '+', 'label_color':'green'}, {'value':abs(item[1][1]),'label' : '-', 'label_color':'red'}]) 
                i += 1
                if i is max_length: break
            #treemap_plotter.render_in_browser()
            #treemap_plotter.render_to_file('processed_data/treemap.svg')
            result_chart = treemap_plotter.render()
            

    def plot_general(self):
        
        values = [0,0]
        perc = [0,0]
        
        for aspect, v, in self.plotter_data.items():
            values[0] += v[0]
            values[1] += abs(v[1])
        
        if(values[0] > 0):
            perc[0] = round(values[0]*100/(values[0]+values[1]),1)
        perc[1] = 100 - perc[0]

        for aspect, v in self.plotter_data.items():
            values[0] += v[0]
            values[1] += abs(v[1])

        pie_plotter = pygal.Pie(inner_radius=.4)
        pie_plotter.add('negativo('+"%.1f"%perc[1]+'%)', values[1])
        pie_plotter.add('positivo('+ "%.1f"%perc[0]+'%)', values[0])
        
        #pie_plotter.render_in_browser()
        #pie_plotter.render_to_file('processed_data/pie.svg')
        result_chart = pie_plotter.render()

    """
