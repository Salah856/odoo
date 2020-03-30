# -*- coding: utf-8 -*-
from odoo import models, fields, api
import time
from datetime import date,datetime
from dateutil.relativedelta import relativedelta
import re
from odoo.exceptions import ValidationError


class hms_patient(models.Model):
    _name = "hospitalms.patient"
    _rec_name = 'fname'
    fname=fields.Char()
    lname=fields.Char()
    birth_date=fields.Date()
    history=fields.Html()
    CR_ratio=fields.Float()
    blood_type=fields.Selection([('A+','A+'),
                                 ('A-','A-'),
                                 ('B+', 'B+'),
                                 ('B-', 'B-'),
                                 ('AB+','AB+'),
                                 ('AB-','AB-'),
                                 ('O+','O+'),
                                 ('O-', 'O-')
                                 ],
                                default="A+")
    PCR=fields.Boolean()
    image=fields.Binary("Image")
    address=fields.Text()
    Age=fields.Integer(compute="compute_age", store=True)
    department_id=fields.Many2one(comodel_name='hospitalms.department')
    department_capacity=fields.Integer(related='department_id.capacity')
    status=fields.Selection([
        ("undetermined",'undetermined'),
        ("good","good"),
        ("fair","fair"),
        ("serious","serious")
    ],default="undetermined")
    doctors=fields.Many2many(comodel_name="hospitalms.doctor")
    logs=fields.One2many(comodel_name="hospitalms.logs",inverse_name="patient_id")
    email=fields.Char()

    def change_status(self):
        if self.status=="undetermined":
            self.status="good"
        elif self.status=="good":
            self.status="fair"
        elif self.status=="fair":
            self.status="serious"
        elif self.status=="serious":
            self.status="undetermined"
        self.logs.create({
           "patient_id": self.id,
           "description": self.fname + "'s status has changed to " + self.status,
        })

    @api.onchange('Age')
    def onchange_age(self):
        if self.Age<30:
            PCR_domain=[('checked','=',True)]
        else:
            PCR_domain=[]
        return {
                'domain':{'history':PCR_domain},
                'warning':{
                    'title':'age change',
                    'message':'PCR has been checked!'
                }
            }

    @api.depends("birth_date")
    def compute_age(self):
        for rec in self:
            if rec.birth_date:
                dt=str(rec.birth_date)
                dob = datetime.strptime(dt, "%Y-%m-%d").date()
                today = date.today()
                relative_data = relativedelta(today, dob)
                rec.Age = int(relative_data.years)


    @api.constrains("email")
    def check_email(self):
        for rec in self:
            if not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", rec.email):
                raise ValidationError("Invalid Email!")


    _sql_constraints = [
        ("valid email",'UNIQUE(email)',"the email you inserted already exists")
    ]



class Doctors(models.Model):
    _name = "hospitalms.doctor"
    _rec_name = 'fname'
    fname=fields.Char()
    lname=fields.Char()
    image=fields.Binary("Image")



class Department(models.Model):
    _name = 'hospitalms.department'
    name=fields.Char()
    capacity=fields.Integer()
    is_open=fields.Boolean()
    patients=fields.One2many(comodel_name="hospitalms.patient",inverse_name="department_id")

class Logs(models.Model):
    _name = 'hospitalms.logs'
    description=fields.Char()
    patient_id=fields.Many2one(comodel_name="hospitalms.patient")
    # _columns = {
    #     'create_date': fields.Datetime('Date Created', readonly=True),
    #     'create_uid': fields.Many2one('res.users', 'by User', readonly=True)
    #     }


class Customers(models.Model):
    _inherit = "res.partner"
    related_patient_id = fields.Many2one("hospitalms.patient")

    @api.constrains("email")
    def check_email(self):
        for rec in self:
            if rec.email:
                patient_emails=self.env['hospitalms.patient'].search([('email', '=',rec.email)])
                if patient_emails:
                    raise ValidationError("there is a patient with this email!")
    @api.multi
    def unlink(self):
        for rec in self:
            if rec.related_patient_id:
                raise ValidationError("you can't delete this user there's a related patient to him!")
        return super().unlink()