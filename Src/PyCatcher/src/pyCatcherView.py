import locale
import gtk 
from xdot import DotWidget
import datetime
import time
from filters import ARFCNFilter, FoundFilter, ProviderFilter

class PyCatcherGUI:
 
    def __init__(self, catcher_controller):
        encoding = locale.getlocale()[1]
        self._utf8conv = lambda x : unicode(x, encoding).encode('utf8')
        
        self._builder = gtk.Builder()
        self._builder.add_from_file('../GUI/catcher_main.glade')
        self._main_window = self._builder.get_object('main_window')
        self._main_window.show()
        
        self._filter_window = self._builder.get_object('filter_window')
                   
        self._catcher_controller = catcher_controller        
        
        self._bs_tree_view = self._builder.get_object('tv_stations')
        self._add_column("Provider", 0)
        self._add_column("ARFCN", 1)
        self._add_column("Strength",2)
        self._add_column("Last seen", 3)
        self._bs_tree_view.set_model(self._catcher_controller.bs_tree_list_data)       
            
        self._horizontal_container = self._builder.get_object('vbox2')
        self._dot_widget = DotWidget()
        self._horizontal_container.pack_start_defaults(self._dot_widget)
        self._dot_widget.set_filter('neato')
        self._dot_widget.show()
        self._dot_widget.connect('clicked', self._on_graph_node_clicked)
        
        self._builder.connect_signals(self)
        
        log_view = self._builder.get_object('te_log')
        self._log_buffer = log_view.get_buffer()        
        self._log_buffer.insert(self._log_buffer.get_end_iter(),self._utf8conv("-- Log execution on " + datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M %p") + "  --\n\n"))
        
        self._main_window.show()         
        
    def _add_column(self, name, index):
        column = gtk.TreeViewColumn(name, gtk.CellRendererText(), text=index)
        column.set_resizable(True)
        column.set_sort_column_id(index)
        self._bs_tree_view.append_column(column)
    
    def _update_filters(self):
        if self._builder.get_object('cb_filter_by_provider').get_active():
            self._catcher_controller.provider_filter.params = {'providers': self._builder.get_object('te_filter_provider').get_text()}
            self._catcher_controller.provider_filter.is_active = True
            print 'provider active'
        else: 
            self._catcher_controller.provider_filter.is_active = False 
            print 'provider off'
                                                               
        if self._builder.get_object('cb_filter_by_arfcn').get_active():
            self._catcher_controller.arfcn_filter.params = {'from':int(self._builder.get_object('te_filter_arfcn_from').get_text()),
                                         'to':int(self._builder.get_object('te_filter_arfcn_to').get_text())}
            self._catcher_controller.arfcn_filter.is_active = True
            print 'arfcn active'
        else:
            self._catcher_controller.arfcn_filter.is_active = False
            print 'arfcn off'
        
        if self._builder.get_object('cb_only_scanned_bs').get_active():
            self._catcher_controller.found_filter.is_active = True
            print 'scanned active'
        else:
            self._catcher_controller.found_filter.is_active = False
            print 'scanned off' 
        
        self._catcher_controller.trigger_redraw()
    
    def _on_graph_node_clicked (self, widget, url, event):
        print 'NODE CLICKED'
    
    def _on_main_window_destroy(self, widget):
        self._catcher_controller.shutdown() 
        gtk.main_quit()
        
    def _on_scan_toggled(self, widget):
        if(widget.get_active()):      
            self._catcher_controller.start_scan()
        else:
            self._catcher_controller.stop_scan()
            
    def _on_firmware_toggled(self, widget):
        if(widget.get_active()):
            self._catcher_controller.start_firmware()
        else:
            self._catcher_controller.stop_firmware()

    def _on_filter_clicked(self,widget):
        self._filter_window.show()

    def _on_filter_close_clicked(self, widget):
        self._update_filters()
        self._filter_window.hide()

    def _on_open_file_clicked(self, widget):
        chooser = gtk.FileChooserDialog(title="Open dot File",
                                        action=gtk.FILE_CHOOSER_ACTION_OPEN,
                                        buttons=(gtk.STOCK_CANCEL,
                                                 gtk.RESPONSE_CANCEL,
                                                 gtk.STOCK_OPEN,
                                                 gtk.RESPONSE_OK))
        chooser.set_default_response(gtk.RESPONSE_OK)
        filter = gtk.FileFilter()
        filter.set_name("Graphviz dot files")
        filter.add_pattern("*.dot")
        chooser.add_filter(filter)
        filter = gtk.FileFilter()
        filter.set_name("All files")
        filter.add_pattern("*")
        chooser.add_filter(filter)
        if chooser.run() == gtk.RESPONSE_OK:
            filename = chooser.get_filename()
            chooser.destroy()
            self.load_dot_from_file(filename)
        else:
            chooser.destroy()
    
    def _on_zoon_in_clicked(self,widget):
        self._dot_widget.on_zoom_in(None)
    
    def _on_zoon_out_clicked(self,widget):
        self._dot_widget.on_zoom_out(None)
    
    def _on_zoon_fit_clicked(self,widget):
        self._dot_widget.on_zoom_fit(None)
    
    def _on_zoon_original_clicked(self,widget):
        self._dot_widget.on_zoom_100(None)
    
    def load_dot_from_file(self, filename):
        try:
            fp = file(filename, 'rt')
            self.load_dot(fp.read(), filename)
            fp.close()
        except IOError, ex:
            self.show_info(ex)
    
    def load_dot(self, dotcode, filename="<stdin>"):
        if self._dot_widget.set_dotcode(dotcode, filename):
            #self._dot_widget.zoom_to_fit()           
            pass
    
    def show_info(self, message, title='PyCatcher', time_to_sleep=3, type='INFO'):
        gtk_type = {'INFO' : gtk.MESSAGE_INFO,
                    'ERROR': gtk.MESSAGE_ERROR}
        
        dlg = gtk.MessageDialog(type=gtk.MESSAGE_INFO,
                                    message_format=str(message)                                
                                    )
        
        dlg.set_title(title)
        dlg.show()
        time.sleep(time_to_sleep)
        dlg.destroy()
    
    def log_line(self, line):
        self._log_buffer.insert(self._log_buffer.get_end_iter(),self._utf8conv(datetime.datetime.now().strftime("%I:%M:%S %p")+ ":     " + line + "\n"))