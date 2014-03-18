# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2013 CERN.
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


from invenio.base.factory import with_app_context
from invenio.testsuite import InvenioTestCase, make_test_suite, \
    run_test_suite


class WorkflowOthers(InvenioTestCase):
    def test_result_abstraction(self):
        from invenio.modules.workflows.utils import BibWorkflowObjectIdContainer
        from invenio.modules.workflows.models import BibWorkflowObject
        from invenio.modules.workflows.worker_result import AsynchronousResultWrapper


        bwoic = BibWorkflowObjectIdContainer(None)
        self.assertEqual(bwoic.get_object(), None)
        test_object = BibWorkflowObject()
        test_object.set_data(45)
        test_object.save()
        bwoic2 = BibWorkflowObjectIdContainer(test_object)
        self.assertEqual(bwoic2.get_object().id, test_object.id)

        result = bwoic2.to_dict()

        self.assertEqual(bwoic2.from_dict(result).id, test_object.id)
        test_object.delete(test_object.id)
        try:
            AsynchronousResultWrapper()
        except Exception as e:
            self.assertEqual(isinstance(e, TypeError), True)

    def test_acces_to_undefineworkflow(self):
        from invenio.modules.workflows.api import start
        from invenio.modules.workflows.errors import WorkflowDefinitionError

        try:
            start("@thisisnotatrueworkflow@", ["my_false_data"], random_kay_args="value")
        except Exception as e:
            self.assertEqual(isinstance(e, WorkflowDefinitionError), True)
            return
        self.assertEqual(False, True)

@with_app_context()
def main():
    """
    Main function which is used to run tests.
    """
    test_suite = make_test_suite(WorkflowOthers)
    run_test_suite(test_suite)


if __name__ == "__main__":
    main()
