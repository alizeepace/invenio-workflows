# -*- coding: utf-8 -*-
## This file is part of Invenio.
## Copyright (C) 2012, 2013 CERN.
##
## Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
"""Holding Pen & BibWorkflow web interface"""

__revision__ = "$Id$"

__lastupdated__ = """$Date$"""

from flask import render_template
from pprint import pformat
from invenio.bibworkflow_model import Workflow, BibWorkflowObject
from invenio.bibworkflow_api import start_delayed
import os
from invenio.pluginutils import PluginContainer
from invenio.config import CFG_PYLIBDIR, CFG_LOGDIR
from invenio.webinterface_handler_flask_utils import _, InvenioBlueprint
from invenio.bibworkflow_utils import get_workflow_definition

import traceback

blueprint = InvenioBlueprint('bibworkflow', __name__,
                             url_prefix="/admin/bibworkflow",
                             menubuilder=[('main.admin.bibworkflow',
                                           _('Configure BibWorkflow'),
                                          'bibworkflow.index')],
                             breadcrumbs=[(_('Administration'),
                                           'help.admin'),
                                          (_('Configure BibWorkflow'),
                                           'bibworkflow.index')],)


@blueprint.route('/', methods=['GET', 'POST'])
@blueprint.route('/index', methods=['GET', 'POST'])
@blueprint.invenio_authenticated
@blueprint.invenio_templated('bibworkflow_index.html')
def index():
    """
    Dispalys main interface of BibWorkflow.
    """
    w = Workflow.query.all()
    return dict(workflows=w)


@blueprint.route('/entry_details', methods=['GET', 'POST'])
@blueprint.invenio_authenticated
@blueprint.invenio_wash_urlargd({'id_entry': (int, 0)})
def entry_details(id_entry):
    """
    Displays entry details.
    """
    wfe_object = BibWorkflowObject.query.filter(BibWorkflowObject.id == id_entry).first()

    return render_template('bibworkflow_entry_details.html',
                           entry=wfe_object, log="",
                           data_preview=_entry_data_preview(wfe_object.data, 'hd'),
                           workflow_func=get_workflow_definition(wfe_object.bwlWORKFLOW.name))


@blueprint.route('/workflow_details', methods=['GET', 'POST'])
@blueprint.invenio_authenticated
@blueprint.invenio_wash_urlargd({'id_workflow': (unicode, "")})
def workflow_details(id_workflow):
    w_metadata = Workflow.query.filter(Workflow.uuid == id_workflow).first()

    return render_template('bibworkflow_workflow_details.html',
                           workflow_metadata=w_metadata,
                           log="",
                           workflow_func=get_workflow_definition(w_metadata.name))


@blueprint.route('/workflows', methods=['GET', 'POST'])
@blueprint.invenio_authenticated
@blueprint.invenio_templated('bibworkflow_workflows.html')
def workflows():
    loaded_workflows = PluginContainer(os.path.join(CFG_PYLIBDIR, 'invenio',
                                       'bibworkflow_workflows', '*.py'))
    open(os.path.join(CFG_LOGDIR, 'broken-bibworkflow-workflows.log'), 'w').\
        write(pformat(loaded_workflows.get_broken_plugins()))

    return dict(workflows=loaded_workflows.get_enabled_plugins(),
                broken_workflows=loaded_workflows.get_broken_plugins())


@blueprint.route('/run_workflow', methods=['GET', 'POST'])
@blueprint.invenio_authenticated
@blueprint.invenio_wash_urlargd({'workflow_name': (unicode, "")})
def run_workflow(workflow_name, data={"data": 10}):
    try:
        print "Starting workflow '%s'" % (workflow_name,)
        start_delayed(workflow_name, data)
    except:
        traceback.print_exc()
    return "Workflow has been started."


@blueprint.route('/entry_data_preview', methods=['GET', 'POST'])
@blueprint.invenio_authenticated
@blueprint.invenio_wash_urlargd({'oid': (int, 0),
                                'of': (unicode, 'default')})
def entry_data_preview(oid, of):
    workflow_object = BibWorkflowObject.query.filter(BibWorkflowObject.id ==
                                                     oid).first()
    return _entry_data_preview(workflow_object.data, of)


def _entry_data_preview(data, of='default'):
    if format == 'hd' or format == 'xm':
        from invenio.bibformat import format_record
        try:
            data['record'] = format_record(recID=None, of=of,
                                           xml_record=data['record'])
        except:
            print "This is not a XML string"
    try:
        return data['record']
    except:
        return data
