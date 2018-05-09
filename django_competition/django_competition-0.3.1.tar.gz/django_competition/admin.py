"""Admin module."""

from django.contrib import admin

from . import models


class CompetitionEntry(admin.TabularInline):
  """Competition Entry in-line admin."""
  model = models.CompetitionEntry

  fields = [
    'name',
    'description',
    'votes',
  ]

  readonly_fields = [
    'votes'
  ]


@admin.register(models.Competition)
class CompetitionAdmin(admin.ModelAdmin):
  """Competition model admin."""

  list_display = [
    'name'
  ]

  fields = [
    'name',
    'description',
    'votes_per_day',
    'entries_per_vote',
    'allow_disposable_emails'
  ]

  inlines = [
    CompetitionEntry
  ]


@admin.register(models.Vote)
class VoteAdmin(admin.ModelAdmin):

  fields = readonly_fields = [
    'entry', 'group'
  ]

  list_display = [
    'entry',
    'vote_competition',
    'vote_email',
    'vote_date'
  ]

  list_filter = (
    'group__competition__name',
  )

  def vote_competition(self, obj):
    return obj.group.competition

  def vote_email(self, obj):
    return obj.group.vote_source

  def vote_date(self, obj):
    return obj.group.date_voted

  vote_competition.admin_order_field = "group__competition"
  vote_email.admin_order_field = "group__vote_source"
  vote_date.admin_order_field = "group__date_voted"
