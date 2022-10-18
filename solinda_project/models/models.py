from odoo import models, fields, api
from dateutil import relativedelta

class ProjectTask(models.Model):
  _inherit = 'project.task'

  change_stage_time = fields.Datetime('Change Stage Time',store=True)
  duration_change_stage = fields.Char(string='Duration')

  @api.onchange('stage_id')
  def _onchange_stagescrm_id(self):
    for i in self:
      i.change_stage_time = fields.datetime.now()
         

  # @api.depends('change_stage_time')
  def _compute_duration_change_stage(self):
    now = fields.datetime.now()
    for i in self:
      if i.change_stage_time:
        diff = relativedelta.relativedelta(i.change_stage_time, now)
        years = diff.years
        months = diff.months
        days = diff.days
        hours = diff.hours
        minutes = diff.minutes
        if years > 0:
          i.duration_change_stage = str(years) + " Tahun " + str(months) + " bulan " + str(days) + " Hari" + str(hours) + " jam " + str(minutes) + " menit"
        elif months > 0:
          i.duration_change_stage = str(months) + " Bulan " + str(days) + " hari " + str(hours) + " jam " + str(minutes) + " menit"
        elif days > 0:
          i.duration_change_stage = str(days) + " Hari " + str(hours) + " jam " + str(minutes) + " menit"
        elif hours > 0:
          i.duration_change_stage = str(hours) + " Jam " + str(minutes) + " menit"
        else:
          i.duration_change_stage =str(minutes) + " Menit " + str(diff.seconds) + " detik"
      else:
          i.duration_change_stage = 'The changes stage time is not defined!'
