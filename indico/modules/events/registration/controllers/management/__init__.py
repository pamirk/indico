# This file is part of Indico.
# Copyright (C) 2002 - 2025 CERN
#
# Indico is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see the
# LICENSE file for more details.

from flask import request
from sqlalchemy.orm import contains_eager, defaultload

from indico.modules.events.management.controllers import RHManageEventBase
from indico.modules.events.registration.controllers import RegistrationFormMixin
from indico.modules.events.registration.lists import RegistrationListGenerator
from indico.modules.events.registration.models.form_fields import RegistrationFormField
from indico.modules.events.registration.models.forms import RegistrationForm
from indico.modules.events.registration.models.registrations import Registration


class RHManageRegFormsBase(RHManageEventBase):
    """Base class for all registration management RHs."""

    PERMISSION = 'registration'


class RHManageRegFormBase(RegistrationFormMixin, RHManageRegFormsBase):
    """Base class for a specific registration form."""

    def _process_args(self):
        RHManageRegFormsBase._process_args(self)
        RegistrationFormMixin._process_args(self)
        self.list_generator = RegistrationListGenerator(regform=self.regform)


class RHManageRegistrationBase(RHManageRegFormBase):
    """Base class for a specific registration."""

    normalize_url_spec = {
        'locators': {
            lambda self: self.registration
        }
    }

    def _process_args(self):
        RHManageRegFormBase._process_args(self)
        self.registration = (Registration.query
                             .filter(Registration.id == request.view_args['registration_id'],
                                     ~Registration.is_deleted,
                                     ~RegistrationForm.is_deleted)
                             .join(Registration.registration_form)
                             .options(contains_eager(Registration.registration_form)
                                      .defaultload('form_items')
                                      .joinedload('children'))
                             .options(defaultload(Registration.data)
                                      .joinedload('field_data'))
                             .one())


class RHManageRegistrationFieldActionBase(RHManageRegFormBase):
    """Base class for a specific registration field."""

    normalize_url_spec = {
        'locators': {
            lambda self: self.field
        },
        'skipped_args': {'section_id'}
    }

    def _process_args(self):
        RHManageRegFormBase._process_args(self)
        self.field = (RegistrationFormField.query
                      .filter(RegistrationFormField.id == request.view_args['field_id'],
                              RegistrationFormField.registration_form == self.regform,
                              RegistrationFormField.is_enabled,
                              ~RegistrationFormField.is_deleted)
                      .one())
