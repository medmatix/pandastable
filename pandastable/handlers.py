#!/usr/bin/env python
"""
    Module for plot viewer event classes.

    Created Jan 2016
    Copyright (C) Damien Farrell

    This program is free software; you can redistribute it and/or
    modify it under the terms of the GNU General Public License
    as published by the Free Software Foundation; either version 2
    of the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

import types
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
#import matplotlib.animation as animation
from collections import OrderedDict
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from matplotlib.text import Text, Annotation
from matplotlib.collections import PathCollection
from matplotlib.backend_bases import key_press_handler

class DragHandler(object):
    """ A simple class to handle picking and dragging"""

    def __init__(self, parent, figure=None):
        """ Create a handler and connect it to the plotviewer figure.
        """

        self.parent = parent
        fig = parent.fig
        # simple attibute to store the dragged text object
        self.dragged = None
        fig.canvas.mpl_connect("pick_event", self.on_pick_event)
        fig.canvas.mpl_connect('button_press_event', lambda event: fig.canvas._tkcanvas.focus_set())
        fig.canvas.mpl_connect("button_release_event", self.on_release_event)
        fig.canvas.mpl_connect("key_press_event", self.key_press_event)
        return

    def on_pick_event(self, event):
        " Store which text object was picked and were the pick event occurs."

        df = self.parent.data
        self.dragged = event.artist

        if isinstance(event.artist, PathCollection):
            ind = event.ind
            print('onpick scatter:', ind, df.ix[ind])
        elif isinstance(event.artist, Line2D):
            thisline = event.artist
            xdata = thisline.get_xdata()
            ydata = thisline.get_ydata()
            ind = event.ind
            print('onpick line:', zip(np.take(xdata, ind), np.take(ydata, ind)))
        elif isinstance(event.artist, Rectangle):
            patch = event.artist
            print('onpick patch:', patch.get_path())
        elif isinstance(self.dragged, Annotation):
            text = event.artist
            print('onpick text:', text.get_text())
            self.selected = text
        return True

    def on_release_event(self, event):
        " Update and store text/annotation position "

        fig = self.parent.fig
        ax = fig.axes[0]
        xy = (event.xdata, event.ydata)
        xyax = fig.transFigure.inverted().transform(xy)
        print (xyax)
        #xy = (event.x, event.y)
        #if annotation object moved we record new coords
        if isinstance(self.dragged, Annotation):
            key = self.dragged._id
            print (self.dragged.get_text(), key)
            d = self.parent.labelopts.textboxes[key]
            #print (d)
            bbox = self.dragged.get_window_extent()
            x = bbox.x0
            y = bbox.y0
            #print (bbox)
            bbdata = ax.transAxes.inverted().transform(bbox)
            #xy = bbdata[0]
            d['coords'] = xy
            print (xy)
        self.dragged = None
        return True

    def key_press_event(self, event):
        """Handle key press"""

        if event.key == 'delete':
            self.selected.set_visible(False)
            fig = self.parent.fig
            fig.canvas.draw()
            key = self.selected._id
            del self.parent.labelopts.textboxes[key]
            self.selected = None

    def disconnect(self):
        """disconnect all the stored connection ids"""

        return