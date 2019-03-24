import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_table
import plotly
import plotly.graph_objs as go

import pandas as pd
import numpy as np
from flask import Flask

import os
import base64
import datetime
import io

from scipy.spatial.distance import cdist

external_css = ["css/style.css",
		"https://cdnjs.cloudflare.com/ajax/libs/skeleton/2.0.4/skeleton.min.css",
                "https://fonts.googleapis.com/css?family=Raleway:400,400i,700,700i",
                "https://fonts.googleapis.com/css?family=Product+Sans:400,400i,700,700i"]

app = dash.Dash(
    name='earthquake-distances-app',
#    sharing=True,
#    url_base_pathname='/earthquake-distances',
    external_stylesheets=external_css
)

app.title="Source-to-Site earthquake distance metrics"

#app.config.update({
    # as the proxy server will remove the prefix
  #  'routes_pathname_prefix': '/earhtquake-distances/',

    # the front-end will prefix this string to the requests
    # that are made to the proxy server
 #   'requests_pathname_prefix': '/earthquake-distances/'
#})


server = app.server

#app.css.config.serve_locally = True
#app.scripts.config.serve_locally = True

def GeoDistance(lat1, lon1, lat2, lon2, unit):
    radlat1 = np.pi * lat1/180
    radlat2 = np.pi * lat2/180
    theta = lon1-lon2
    radtheta = np.pi * theta/180
    dist = np.sin(radlat1) * np.sin(radlat2) + np.cos(radlat1) * np.cos(radlat2) * np.cos(radtheta);
    dist = np.arccos(dist)
    dist = dist * 180/np.pi
    dist = dist * 60 * 1.1515

    if unit=="K":
            dist = dist * 1.609344
    if unit=="N":
            dist = dist * 0.8684
    return dist


def EQDistances(points,EQDEPTH,Strike,Dip,Length,Width,DeltaL,DeltaW):
#TODO: DeltaL, DeltaW

    dip = np.radians(-Dip)
    strike = np.radians(Strike-90)

    cosDip, cosStrike, sinDip, sinStrike = np.cos(dip), np.cos(strike), np.sin(dip), np.sin(strike)

    rotationStrike = np.array([[cosStrike, -sinStrike, 0],
                               [sinStrike, cosStrike, 0],
                               [0,0,1]]
                             )


    rotationDip = np.array([[cosDip, 0, -sinDip],
                           [0, 1, 0],
                           [sinDip,0,cosDip]]
                          )

    #DISTANCE CALCULATIONS
    repi = np.sqrt(np.sum(points**2, axis = 1))
    rhyp = np.sqrt(repi**2+EQDEPTH**2)

    eqDimensions = np.array([Width/2,Length/2,0])
    eqDimensionsSurface = eqDimensions * np.array([np.cos(Dip),1,1])

    ### RJB
    #rotate eventcoords back strikewise
    #so that cases become easy to check
    points = np.array(points).dot(rotationStrike)
    diff = np.abs(points) - eqDimensionsSurface

    rjb = np.sqrt((((np.abs(diff) + diff)/2)**2).sum(axis=1))
    ### RRUP
    #rotate eventcoords back dipwise
    #so that cases become easy to check
    points = (np.array(points)+np.array([0,0,EQDEPTH])).dot(rotationDip)
    diff = np.abs(points) - eqDimensions

    rrup = np.sqrt((((np.abs(diff) + diff)/2)**2).sum(axis=1))
    
    rell = cdist(points, np.array([eqDimensions*np.array([-1,1,1]),
                                eqDimensions*np.array([-1,-1,1])])).mean(axis=1)

    rz = cdist(points, np.array([eqDimensions*np.array([1,1,1]),
                                eqDimensions*np.array([-1,1,1]),
                                eqDimensions*np.array([-1,-1,1]),
                                eqDimensions*np.array([1,-1,1])])).mean(axis=1)

    return (repi,rhyp,rjb,rrup,rell,rz)



def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return html.Div([
        html.H5(filename),
        html.H6(datetime.datetime.fromtimestamp(date)),

        dash_table.DataTable(
            data=df.to_dict('rows'),
            columns=[{'name': i, 'id': i} for i in df.columns]
        ),

        html.Hr(),  # horizontal line

        # For debugging, display the raw contents provided by the web browser
        html.Div('Raw Content'),
        html.Pre(contents[0:200] + '...', style={
            'whiteSpace': 'pre-wrap',
            'wordBreak': 'break-all'
        })
    ])




app.layout = html.Div([
    ############################
    #CONTROLS
	html.Div([html.H1(children='Source-to-Site earthquake distances'),
                html.Div([
			html.Div([
				html.Label('EQLAT'),
	                        dcc.Input(
					id='EQLAT',
					placeholder='Source Latitude', 
			     		value='5.0',
        		      		type="text"
					),
				html.Label('EQLON Input'),
                    		dcc.Input(
					id='EQLON',
					placeholder='Source Longitude', 
					value='5.0', 
					type="text"
					),
				html.Label('EQDEPTH Input'),
                    		dcc.Input(
					id='EQDEPTH', 
					placeholder='Source Depth',
					value='10.0', 
					type="text"
					)
				],
				style={'width': '20%', 
					'display': 'inline-block'}
				),
			html.Div([
				html.Label('SiteLAT Input'),
	 	                dcc.Input(
					id='EVENTLAT',
					placeholder='Site Latitude',
					value='5.0', 
					type="text"
					),
				html.Label('SiteLON Input'),
         		        dcc.Input(
					id='EVENTLON',
					placeholder='Site Longitude',
					value='5.0', 
					type="text"
					)
				],
				style={'width': '20%', 
					'display': 'inline-block'}
				),
			html.Div([
				html.Label('Width'),
		     		dcc.Slider(
                       			id='Width',
                       			min=0,
                       			max=100,
                       			value=5.0,
                      	 		step=1,
					marks={
						'0': '0', 
						'50':'50',
						'100': '100'
						}
	                	       ),
#				html.Br(),
#				html.Label('DeltaW'),
#				dcc.Slider(
 #       	        	        id='DeltaW',
  #      	        	        min=0,
   #     	        	        max=10,
    #    	        	        value=0,
     #   	        	        step=1,
	#				marks={
	#					'0': '0',
	#					'10': '10'
	#					}
	 #               	        ),
				html.Br(),
				html.Label('Length'),
				dcc.Slider(
	                	        id='Length',
	                	        min=0,
	                	        max=100,
	                	        value=20.0,
	                	        step=1,
					marks={
						'0': '0',  
						'50':'50',
						'100': '100'
						}
	                	        ),
	#			html.Br(),
	#			html.Label('DeltaL'),
	#	     		dcc.Slider(
         #               		id='DeltaL',
          #              		min=0,
           #             		max=10,
            #            		value=0,
             #           		step=1,
		#			marks={
		#				'0': '0', 
		#				'10': '10'
		#				}
                 #       		)
				html.Br(),
				html.Label('Strike'),
	               		dcc.Slider(
        	        	        id='Strike',
        	        	        min=0,
        	        	        max=360,
        	        	        value=10.0,
        	        	        step=1,
					marks={
						'0': '0', 
						'90': '90', 
						'180': '180', 
						'270': '270',
						'360':'360'
						}
                        	),
				html.Br(),
				html.Label('Dip'),
	                	dcc.Slider(
        	        	        id='Dip',
        	        	        min=0,
        	        	        max=90,
        	        	        value=45,
        	        	        step=1,
					marks={
						'0': '0',
						'30': '30', 
						'60': '60', 
						'90': '90'
						}
        	        	        )
				],
				style={ 'height': '30%',
					'width': '49%', 
					'display': 'inline-block'
					}
				)#,
#			html.Div([
#				html.Br(),
#				html.Label('Strike'),
#	               		dcc.Slider(
 #       	        	        id='Strike',
  #      	        	        min=0,
   #     	        	        max=360,
    #    	        	        value=10.0,
     #   	        	        step=1,
	#				marks={
	#					'0': '0', 
	#					'90': '90', 
	#					'180': '180', 
	#					'270': '270',
	#					'360':'360'
	#					}
         #               	),
	#			html.Br(),
	#			html.Label('Dip'),
	 #               	dcc.Slider(
        #	        	        id='Dip',
        #	        	        min=0,
        #	        	        max=90,
        #	        	        value=45,
        #	        	        step=1,
	#				marks={
	#					'0': '0',
	#					'30': '30', 
	#					'60': '60', 
	#					'90': '90'
	#					}
        #	        	        )
	#			],
	#			style={'width': '49%', 
	#				'display': 'inline-block'
	#				}
	#		)
                    ],
                style={
			'width': '98%', 
			'display': 'inline-block'
			}
		),
		html.Br(),
		html.Br(),
                #VALUES
                html.Div(id='distance-text'),

		html.Div([
			dcc.Graph(
				#figure=figure,
				 id='distance-simulation'
        	                )
			],
        		style={
				'display': 'inline-block', 
				'width': '19%'
				}
	                )
		],
                    style={
			'display': 'inline-block', 
			'width': '49%'
			}
		),
                #####################################
                #Graphics
                html.Div([
                    dcc.Graph(
			 id='contour-of-distance'
                	)
			],
                style={'float':'right',
                    'display': 'inline-block',
                    'width': '49%'
			}
                ),
		html.Br(),
		html.Div([
			dcc.Upload(
        			id='upload-data',
       				 children=html.Div([
       					     'Drag and Drop or ',
       					     html.A('Select Files')
      						  ]),
      				style={
            				'width': '100%',
            				'height': '60px',
            				'lineHeight': '60px',
           				'borderWidth': '1px',
            				'borderStyle': 'dashed',
           				'borderRadius': '5px',
            				'textAlign': 'center',
            				'margin': '10px'
        				},
       			# Allow multiple files to be uploaded
        			multiple=True
    				),
    			html.Div(id='output-data-upload'),
			],
 			style={
                    		'display': 'inline-block',
                    		'width': '99%'
			}
		)
	])



@app.callback(
    dash.dependencies.Output('contour-of-distance', 'figure'),
    [
#    dash.dependencies.Input('distance','value'),
    dash.dependencies.Input('EVENTLAT','value'),
    dash.dependencies.Input('EVENTLON','value'),
    dash.dependencies.Input('EQDEPTH','value'),
    dash.dependencies.Input('Width','value'),
 #   dash.dependencies.Input('DeltaW','value'),
    dash.dependencies.Input('Length','value'),
#    dash.dependencies.Input('DeltaL','value'),
    dash.dependencies.Input('Strike','value'),
    dash.dependencies.Input('Dip','value')
    ])

#def update_graph(EVENTLAT,EVENTLON,EQDEPTH,Width,DeltaW,Length,DeltaL,Strike,Dip):
def update_graph(EVENTLAT,EVENTLON,EQDEPTH,Width,Length,Strike,Dip):

    EQDEPTH= float(EQDEPTH)
    EVENTLAT= float(EVENTLAT)
    EVENTLON= float(EVENTLON)
    Width= float(Width)
    Length= float(Length)
 #   DeltaW= float(DeltaW)
  #  DeltaL= float(DeltaL)
    Strike= float(Strike)
    Dip= float(Dip)

    # DISTANCE CALCULATIONS

    X = np.arange(-50,50, 1)
    Y = np.arange(-50,50, 1)

    points = [(x, y,z) for x in X for y in Y for z in range(1)]

    #metrics = np.empty([x.size(), y.size(),5])
    metrics = EQDistances(np.array(points), EQDEPTH,Strike,Dip,Length,Width,0,0)

#    distances = {
#        "Epicentral Distance Repi": metrics[0],
#        "Hypocentral Distance Rhypo": metrics[1],
#        "Joyner-Boore Distance Rjb":metrics[2],
#        "Rupture Distance Rrup":metrics[3],
#	"Ellipse Distance Rell":metrics[4],
#        "Schwarz/Mean Fault Distance Rz":metrics[5]
#        }

    contoursDict = dict(start=0,
	  	        end=70,
		    	size=5,
			coloring ='heatmap',
            		showlabels = True,
            		labelfont = dict(
               			family = 'Raleway',
                		size = 12,
                		color = 'white')
			)

    colorBarDict=dict(
            	title='Distance [km]',
            	titleside='top',
		x=1.2,
		#xpad=100,
            	titlefont=dict(
                	size=14,
                	family='Arial, sans-serif'
	            	)
        	)

    autoContour=False

    trace0 = go.Contour(
		x = X,
                y = Y,
                z=metrics[0].reshape(len(X),len(Y)),
                colorscale='Jet',#reversescale=True,
		autocontour=autoContour,
	        contours=contoursDict,
		colorbar = colorBarDict
		)
    trace1 = go.Contour(
		x = X,
                y = Y,
                z=metrics[1].reshape(len(X),len(Y)),
		xaxis='x1',
  		yaxis='y1',
                colorscale='Jet',#reversescale=True,
		autocontour=autoContour,
	        contours=contoursDict,
		showscale=False
		)
    trace2 = go.Contour(
		x = X,
                y = Y,
                z=metrics[2].reshape(len(X),len(Y)),
		xaxis='x2',
  		yaxis='y2',
                colorscale='Jet',#reversescale=True,
		autocontour=autoContour,
	        contours=contoursDict,
		showscale=False
		)
    trace3 = go.Contour(
		x = X,
                y = Y,
                z=metrics[3].reshape(len(X),len(Y)),
		xaxis='x3',
  		yaxis='y3',
                colorscale='Jet',#reversescale=True,
		autocontour=autoContour,
	        contours=contoursDict,
		showscale=False
		)
    trace4 = go.Contour(
		x = X,
                y = Y,
                z=metrics[4].reshape(len(X),len(Y)),
		xaxis='x4',
  		yaxis='y4',
                colorscale='Jet',#reversescale=True,
		autocontour=autoContour,
	        contours=contoursDict,
		showscale=False
		)
    trace5 = go.Contour(
		x = X,
                y = Y,
                z=metrics[5].reshape(len(X),len(Y)),
		xaxis='x5',
  		yaxis='y5',
                colorscale='Jet',#reversescale=True,
		autocontour=autoContour,
	        contours=contoursDict,
		showscale=False
		)

#	data = [trace0,trace1,trace2,trace3,trace4,trace5]
#
#	layout = go.Layout(
#			xaxis={
#	                       'type': 'linear',
#	                       'title': 'x [km]'
 #                       },
  #        	        yaxis={
   #             	        'title': 'y [km]'
	#		},
    	#	)


    fig = plotly.tools.make_subplots(
		rows=3, 
		cols=2, 
                horizontal_spacing = 0.1,
                vertical_spacing = 0.1,
		subplot_titles=(
			"Epicentral Distance Repi",
        		"Hypocentral Distance Rhypo",
			"Joyner-Boore Distance Rjb",
		        "Rupture Distance Rrup",
			"Ellipse Distance Rell",
		        "Schwarz Distance Rz"
			)
		)

    fig.append_trace(trace0, 1, 1)
    fig.append_trace(trace1, 1, 2)
    fig.append_trace(trace2, 2, 1)
    fig.append_trace(trace3, 2, 2)
    fig.append_trace(trace4, 3, 1)
    fig.append_trace(trace5, 3, 2)
	
    fig['layout'].update(
			height=800, 
			width=700, 
			title='Comparison of spatial Distance Distribution',
			autosize=False,
			scene=dict(
				aspectmode="data"
				)
			)

    return fig
#    return {
#        'data': [
#            go.Contour(
#                x = X,
#                y = Y,
#                z=distances[distance].reshape(len(X),len(Y)),
#                colorscale='Jet'
#                )
#            ],
 #           'layout':
 #               go.Layout(
  #                  xaxis={
   #                    'type': 'linear',
    #                    'title': 'x [km]'
     #                   },
      #              yaxis={
       #                 'title': 'y [km]'},
        #            margin={
         #               'l': 40,
          #              'b': 30,
           #             't': 10,
            #            'r': 0
             #           },
              #      height=400,
               #     width=500,
                #    legend={
                 #       'x': 0,
                  #      'y': 1
                   #     },
                    #hovermode='closest'
                #)
            #}




@app.callback(
    dash.dependencies.Output('distance-simulation', 'figure'),
    [
        dash.dependencies.Input('EQLAT','value'),
        dash.dependencies.Input('EQLON','value'),
        dash.dependencies.Input('EQDEPTH','value'),
        dash.dependencies.Input('EVENTLAT','value'),
        dash.dependencies.Input('EVENTLON','value'),
        dash.dependencies.Input('Width','value'),
#        dash.dependencies.Input('DeltaW','value'),
        dash.dependencies.Input('Length','value'),
#        dash.dependencies.Input('DeltaL','value'),
        dash.dependencies.Input('Strike','value'),
        dash.dependencies.Input('Dip','value')
    ]
)




#def update_simulation(EQLAT,EQLON,EQDEPTH,EVENTLAT,EVENTLON,Width,DeltaW,Length,DeltaL,Strike,Dip):
def update_simulation(EQLAT,EQLON,EQDEPTH,EVENTLAT,EVENTLON,Width,Length,Strike,Dip):
    EQLAT = float(EQLAT)
    EQLON= float(EQLON)
    EQDEPTH= float(EQDEPTH)
    EVENTLAT= float(EVENTLAT)
    EVENTLON= float(EVENTLON)
    Width= float(Width)
    Length= float(Length)
  #  DeltaW= float(DeltaW)
   # DeltaL= float(DeltaL)
    Strike= np.deg2rad(float(Strike))
    Dip= np.deg2rad(float(Dip))

    XEvent= GeoDistance(EQLAT,EVENTLON,EQLAT,EQLON,"K")
    YEvent= GeoDistance(EVENTLAT,EQLON,EQLAT,EQLON,"K")

    #azimuthX = np.arccos(XEvent/repi)
    #azimuthY = np.arccos(YEvent/repi)

    plane=np.array(
			[
				[Width, -Width, -Width, Width],
				[Length, Length, -Length, -Length],
			   	[0,	0,	 0, 	0]
			]
		)/2


    cosDip, cosStrike, sinDip, sinStrike = np.cos(Dip), np.cos(Strike), np.sin(Dip), np.sin(Strike)

    rotationStrike = np.array(
				[
					[cosStrike, -sinStrike, 0],
					[sinStrike, cosStrike, 0],
					[0,	0,	1]]
                             )


    rotationDip = np.array(
				[
					[cosDip, 0, -sinDip],
                           		[0,	 1, 	0],
                           		[sinDip,0,cosDip]
				]
                          )

    planeTransformedStrike = plane.T.dot(rotationStrike).T
    planeTransformedDip = plane.T.dot(rotationDip).T		

    depthArray = np.array(
				[
				[0, 		0,	 0, 	0], 
				[0,		0,	 0, 	0], 
				[EQDEPTH, EQDEPTH, EQDEPTH, EQDEPTH]
				]
			)

    planeTransformed = planeTransformedDip.T.dot(rotationStrike).T - depthArray
    
    name = 'eye = (x:0.1, y:0.1, z:1)'
    camera = dict(
        up=dict(
	    x=0, 
	    y=0, 
	    z=1
	),
        center=dict(
	    x=0, 
	    y=0, 
	    z=0
	),
        eye=dict(
	    x=0.1, 
	    y=0.1, 
	    z=1
	)
    )

#	fig['layout'].update(
#    scene=dict(camera=camera),
#    title=name
#)
    markerSize = 12

    return {
        'data': [
        #STATION
            go.Scatter3d(
                x=[XEvent],
                y=[YEvent],
                z=[0],
                mode='markers',
                marker=dict(
                    size=markerSize,
                    opacity=0.9
                    ),
		name="station",
                showlegend=True
                            ),
            go.Scatter3d(
                #EPICENTRE
                x=[0],
                y=[0],
                z=[0],
                mode='markers',
                marker=dict(
                    size=markerSize,
                    opacity=0.9
                    ),
		name="epicentre",
                showlegend=True
                ),
            go.Scatter3d(
                #HYPOCENTRE
                x=[0],
                y=[0],
                z=[-EQDEPTH],
                mode='markers',
                marker=dict(
                    size=markerSize,
                    opacity=0.
                     ),
		name="hypocentre",
                showlegend=True
                ),
            go.Scatter3d(
            #surfacepolygonpoints
               	x=planeTransformedStrike[0,:],
		y=planeTransformedStrike[1,:],
		z=planeTransformedStrike[2,:],
                mode='markers',
                marker=dict(
                    size=1,
                    opacity=0.9
                ),
                showlegend=False
                ),
            go.Scatter3d(
            #faultpolygonpoints
                x=planeTransformed[0,:],
		y=planeTransformed[1,:],
		z=planeTransformed[2,:],
                mode='markers',
                marker=dict(
                    size=1,
                    opacity=0.9
                    ),
                showlegend=False
                ),

            #PLANES
            go.Mesh3d(
                x=planeTransformedStrike[0,:],
		y=planeTransformedStrike[1,:],
		z=planeTransformedStrike[2,:]
            ),
            go.Mesh3d(
                x=planeTransformed[0,:],
		y=planeTransformed[1,:],
		z=planeTransformed[2,:]
            )
        ],
        'layout': go.Layout(
            scene ={
                'aspectmode':"cube",
                'aspectratio':{
                    'x':1,
                    'y':1,
                    'z':1
                },
                'xaxis':{
                    'title': 'x [km]',
                    'range': [-100, 100]
                    },
                'yaxis':{
                    'title': 'y [km]',
                    'range': [-100, 100],
                    },
                'zaxis':{
                    'title': 'z [km]',
                    'range': [-20, 10],
                    },
		'camera':{
		    'up':{'x':0, 'y':0, 'z':1},
		    'center':{'x':0, 'y':0, 'z':0},
		    'eye':{'x':0.1, 'y':0.1, 'z':1}
			}
                },

                margin={
                        'l': 40,
                        'b': 30,
                        't': 0,
                        'r': 0
                        },
                height=450,
                width=800,
                hovermode='closest'
        )
    }





@app.callback(
    dash.dependencies.Output('distance-text', 'children'),
    [
        dash.dependencies.Input('EQLAT','value'),
        dash.dependencies.Input('EQLON','value'),
        dash.dependencies.Input('EQDEPTH','value'),
        dash.dependencies.Input('EVENTLAT','value'),
        dash.dependencies.Input('EVENTLON','value'),
        dash.dependencies.Input('Width','value'),
       # dash.dependencies.Input('DeltaW','value'),
        dash.dependencies.Input('Length','value'),
      #  dash.dependencies.Input('DeltaL','value'),
        dash.dependencies.Input('Strike','value'),
        dash.dependencies.Input('Dip','value')
    ]
)

#def update_text(EQLAT,EQLON,EQDEPTH,EVENTLAT,EVENTLON,Width,DeltaW,Length,DeltaL,Strike,Dip):
def update_text(EQLAT,EQLON,EQDEPTH,EVENTLAT,EVENTLON,Width,Length,Strike,Dip):
    EQLAT = float(EQLAT)
    EQLON= float(EQLON)
    EQDEPTH= float(EQDEPTH)
    EVENTLAT= float(EVENTLAT)
    EVENTLON= float(EVENTLON)
    Width= float(Width)
    Length= float(Length)
  #  DeltaW= float(DeltaW)
   # DeltaL= float(DeltaL)
    Strike= float(Strike)
    Dip= float(Dip)

    XEvent= GeoDistance(EQLAT,EVENTLON,EQLAT,EQLON,"K")
    YEvent= GeoDistance(EVENTLAT,EQLON,EQLAT,EQLON,"K")

    points = np.array([[XEvent, YEvent, 0]])

    distances = EQDistances(points,EQDEPTH,Strike,Dip,Length,Width,0,0)

    return (
            'Repi: {:.3f} km\n'.format(float(distances[0]))+
           ' Rhyp: {:.3f} km\n'.format(float(distances[1]))+
           ' Rjb: {:.3f} km\n'.format(float(distances[2]))+
           ' Rrup: {:.3f} km\n'.format(float(distances[3]))+
	   ' Rell: {:.3f} km\n'.format(float(distances[4]))+
           ' Rz: {:.3f} km'.format(float(distances[5]))
           )


@app.callback(Output('output-data-upload', 'children'),
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename'),
               State('upload-data', 'last_modified')])
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children



if __name__ == '__main__':
    app.run_server(debug=True)
#    app.run_server(debug=True, host='127.0.0.1', port=6000)
