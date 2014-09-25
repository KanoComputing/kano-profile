/*
* kano_profile.c
*
* Copyright (C) 2014 Kano Computing Ltd.
* License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
*
*/

#include <gtk/gtk.h>
#include <gdk/gdk.h>
#include <glib/gi18n.h>
#include <gdk-pixbuf/gdk-pixbuf.h>
#include <gio/gio.h>

#include <lxpanel/plugin.h>

#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#include <time.h>

#include <kdesk-hourglass.h>

#define NO_LOGIN_ICON "/usr/share/kano-profile/icon/profile-not-login-widget.png"
#define LOGIN_ICON "/usr/share/kano-profile/icon/profile-login-widget.png"
#define SYNC_ICON "/usr/share/kano-profile/icon/widget-sync.png"
#define BACKUP_ICON "/usr/share/kano-profile/icon/widget-backup.png"
#define RESTORE_ICON "/usr/share/kano-profile/icon/widget-restore.png"

#define INTERNET_CMD "/usr/bin/is_internet"
#define SETTINGS_CMD "sudo /usr/bin/kano-settings 4"
#define REGISTER_CMD "/usr/bin/kano-profile-cli is_registered"
#define LOGIN_CMD "/usr/bin/kano-login"
#define PROFILE_CMD "/usr/bin/kano-profile-gui"
#define SYNC_CMD "/usr/bin/kano-sync -d "
#define SOUND_CMD "/usr/bin/aplay /usr/share/kano-media/sounds/kano_open_app.wav"

#define PLUGIN_TOOLTIP "Profile"

#define MINUTE 60

Panel *panel;

typedef struct {
    int log_in;
    GtkWidget *icon;
    guint timer;
} kano_profile_plugin_t;

static gboolean show_menu(GtkWidget*, GdkEventButton*, kano_profile_plugin_t*);
static GtkWidget* get_resized_icon(const char* filename);
static void selection_done(GtkWidget *);
static void popup_set_position(GtkWidget *, gint *, gint *, gboolean *, GtkWidget *);
static gboolean profile_status(kano_profile_plugin_t*);

static int plugin_constructor(Plugin *p, char **fp)
{
    (void)fp;

    panel = p->panel;

    /* allocate our private structure instance */
    kano_profile_plugin_t* plugin = g_new0(kano_profile_plugin_t, 1);
    plugin->log_in = 0;
    /* create an icon */
    GtkWidget *icon = gtk_image_new_from_file(LOGIN_ICON);
    plugin->icon = icon;
    plugin->timer = g_timeout_add(5 * MINUTE * 1000, (GSourceFunc) profile_status, (gpointer) plugin);

    /* put it where it belongs */
    p->priv = plugin;
    /* need to create a widget to show */
    p->pwid = gtk_event_box_new();

    // Check status
    profile_status(plugin);

    /* set border width */
    gtk_container_set_border_width(GTK_CONTAINER(p->pwid), 0);

    /* add the label to the container */
    gtk_container_add(GTK_CONTAINER(p->pwid), GTK_WIDGET(icon));

    /* our widget doesn't have a window... */
    gtk_widget_set_has_window(p->pwid, FALSE);

    gtk_signal_connect(GTK_OBJECT(p->pwid), "button-press-event", GTK_SIGNAL_FUNC(show_menu), p->priv);

    /* Set a tooltip to the icon to show when the mouse sits over the it */
    GtkTooltips *tooltips;
    tooltips = gtk_tooltips_new();
    gtk_tooltips_set_tip(tooltips, GTK_WIDGET(icon), PLUGIN_TOOLTIP, NULL);

    gtk_widget_set_sensitive(icon, TRUE);

    /* show our widget */
    gtk_widget_show_all(p->pwid);

    return 1;
}

static void plugin_destructor(Plugin *p)
{
    kano_profile_plugin_t* plugin = (kano_profile_plugin_t*)p->priv;
    /* Disconnect the timer. */
    g_source_remove(plugin->timer);

    g_free(plugin);
}

static gboolean profile_status(kano_profile_plugin_t *plugin)
{
    // Check if user is log in or not
    plugin->log_in = system(REGISTER_CMD);
    // Update widget icon depending on profile status
    if (plugin->log_in == 0) {
        gtk_image_set_from_file(GTK_IMAGE(plugin->icon), NO_LOGIN_ICON);
    }
    else {
        gtk_image_set_from_file(GTK_IMAGE(plugin->icon), LOGIN_ICON);
    }

    return (plugin->log_in != 0);
}

static void launch_cmd(const char *cmd, const char *appname)
{
    GAppInfo *appinfo = NULL;
    gboolean ret = FALSE;

    if (appname) {
        kdesk_hourglass_start((char *) appname);
    }

    appinfo = g_app_info_create_from_commandline(cmd, NULL, G_APP_INFO_CREATE_NONE, NULL);

    if (appinfo == NULL) {
        perror("Command lanuch failed.");
        if (appname) {
            kdesk_hourglass_end();
        }
        return;
    }

    ret = g_app_info_launch(appinfo, NULL, NULL, NULL);
    if (!ret)
        perror("Command launch failed.");
}

void profile_clicked(GtkWidget* widget, const char* func)
{
    /* Launch /usr/bin/kano-sync -d + func (sync/back-up/restore) */
    char cmd[100];
    strcpy(cmd, SYNC_CMD);
    strcat(cmd, func);
    launch_cmd(cmd, NULL);
}

void login_clicked(GtkWidget* widget)
{
    // Find out if we are online first
    int rc = system (INTERNET_CMD);
    if (rc != -1 && WEXITSTATUS(rc) != 0)
    {
        /* Launch WiFi UI */
        launch_cmd (SETTINGS_CMD, "kano-settings");
        /* Play sound */
        launch_cmd(SOUND_CMD, NULL);
    }
    else
    {
        /* Launch Login UI */
        launch_cmd(LOGIN_CMD, "kano-login");
        /* Play sound */
        launch_cmd(SOUND_CMD, NULL);
    }
}

void launch_profile_clicked(GtkWidget* widget)
{
    /* Launch Porfile UI */
    launch_cmd(PROFILE_CMD, "kano-profile-gui");
    /* Play sound */
    launch_cmd(SOUND_CMD, NULL);
}

static gboolean show_menu(GtkWidget *widget, GdkEventButton *event, kano_profile_plugin_t *plugin)
{
    GtkWidget *menu = gtk_menu_new();
    GtkWidget *header_item;

    if (event->button != 1)
        return FALSE;

    /* Create the menu items */
    header_item = gtk_menu_item_new_with_label("Profile");
    gtk_widget_set_sensitive(header_item, FALSE);
    gtk_menu_append(GTK_MENU(menu), header_item);
    gtk_widget_show(header_item);

    gboolean log_in = profile_status(plugin);

    if (log_in) {
        /* Sync */
        GtkWidget* sync_item = gtk_image_menu_item_new_with_label("Sync");
        g_signal_connect(sync_item, "activate", G_CALLBACK(profile_clicked), "--sync");
        gtk_menu_append(GTK_MENU(menu), sync_item);
        gtk_widget_show(sync_item);
        gtk_image_menu_item_set_image(GTK_IMAGE_MENU_ITEM(sync_item), get_resized_icon(SYNC_ICON));
        /* Back-up */
        GtkWidget* backup_item = gtk_image_menu_item_new_with_label("Back Up");
        g_signal_connect(backup_item, "activate", G_CALLBACK(profile_clicked), "--backup");
        gtk_menu_append(GTK_MENU(menu), backup_item);
        gtk_widget_show(backup_item);
        gtk_image_menu_item_set_image(GTK_IMAGE_MENU_ITEM(backup_item), get_resized_icon(BACKUP_ICON));
        /* Restore */
        GtkWidget* restore_item = gtk_image_menu_item_new_with_label("Restore");
        g_signal_connect(restore_item, "activate", G_CALLBACK(profile_clicked), "--restore");
        gtk_menu_append(GTK_MENU(menu), restore_item);
        gtk_widget_show(restore_item);
        gtk_image_menu_item_set_image(GTK_IMAGE_MENU_ITEM(restore_item), get_resized_icon(RESTORE_ICON));
        /* Profile */
        GtkWidget* profile_item = gtk_image_menu_item_new_with_label("Profile");
        g_signal_connect(profile_item, "activate", G_CALLBACK(launch_profile_clicked), NULL);
        gtk_menu_append(GTK_MENU(menu), profile_item);
        gtk_widget_show(profile_item);
        gtk_image_menu_item_set_image(GTK_IMAGE_MENU_ITEM(profile_item), get_resized_icon(LOGIN_ICON));
    }
    else {
        /* Login app */
        GtkWidget* login_item = gtk_image_menu_item_new_with_label("Log in");
        g_signal_connect(login_item, "activate", G_CALLBACK(login_clicked), NULL);
        gtk_menu_append(GTK_MENU(menu), login_item);
        gtk_widget_show(login_item);
        gtk_image_menu_item_set_image(GTK_IMAGE_MENU_ITEM(login_item), get_resized_icon(LOGIN_ICON));
    }

    g_signal_connect(menu, "selection-done", G_CALLBACK(selection_done), NULL);

    /* Show the menu. */
    gtk_menu_popup(GTK_MENU(menu), NULL, NULL,
               (GtkMenuPositionFunc) popup_set_position, widget,
               event->button, event->time);

    return TRUE;
}

static GtkWidget* get_resized_icon(const char* filename)
{
    GError *error = NULL;
    GdkPixbuf* pixbuf = gdk_pixbuf_new_from_file_at_size (filename, 40, 40, &error);
    return gtk_image_new_from_pixbuf(pixbuf);
}

static void selection_done(GtkWidget *menu)
{
    gtk_widget_destroy(menu);
}

/* Helper for position-calculation callback for popup menus. */
void lxpanel_plugin_popup_set_position_helper(Panel * p, GtkWidget * near,
    GtkWidget * popup, GtkRequisition * popup_req, gint * px, gint * py)
{
    /* Get the origin of the requested-near widget in
screen coordinates. */
    gint x, y;
    gdk_window_get_origin(GDK_WINDOW(near->window), &x, &y);

    /* Doesn't seem to be working according to spec; the allocation.x
sometimes has the window origin in it */
    if (x != near->allocation.x) x += near->allocation.x;
    if (y != near->allocation.y) y += near->allocation.y;

    /* Dispatch on edge to lay out the popup menu with respect to
the button. Also set "push-in" to avoid any case where it
might flow off screen. */
    switch (p->edge)
    {
        case EDGE_TOP: y += near->allocation.height; break;
        case EDGE_BOTTOM: y -= popup_req->height; break;
        case EDGE_LEFT: x += near->allocation.width; break;
        case EDGE_RIGHT: x -= popup_req->width; break;
    }
    *px = x;
    *py = y;
}

/* Position-calculation callback for popup menu. */
static void popup_set_position(GtkWidget *menu, gint *px, gint *py,
                gboolean *push_in, GtkWidget *p)
{
    /* Get the allocation of the popup menu. */
    GtkRequisition popup_req;
    gtk_widget_size_request(menu, &popup_req);

    /* Determine the coordinates. */
    lxpanel_plugin_popup_set_position_helper(panel, p, menu, &popup_req, px, py);
    *push_in = TRUE;
}

static void plugin_configure(Plugin *p, GtkWindow *parent)
{
  // doing nothing here, so make sure neither of the parameters
  // emits a warning at compilation
  (void)p;
  (void)parent;
}

static void plugin_save_configuration(Plugin *p, FILE *fp)
{
  // doing nothing here, so make sure neither of the parameters
  // emits a warning at compilation
  (void)p;
  (void)fp;
}

/* Plugin descriptor. */
PluginClass kano_profile_plugin_class = {
    // this is a #define taking care of the size/version variables
    PLUGINCLASS_VERSIONING,

    // type of this plugin
    type : "kano_profile",
    name : N_("Kano Profile"),
    version: "1.0",
    description : N_("Kano Profile."),

    // we can have many running at the same time
    one_per_system : FALSE,

    // can't expand this plugin
    expand_available : FALSE,

    // assigning our functions to provided pointers.
    constructor : plugin_constructor,
    destructor : plugin_destructor,
    config : plugin_configure,
    save : plugin_save_configuration
};
