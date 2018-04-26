from django.contrib import admin
from election.models import CandidateElection


class CandidateElectionInline(admin.StackedInline):
    model = CandidateElection
    extra = 0


class ElectionAdmin(admin.ModelAdmin):
    list_display = (
        'race', 'election_date', 'division', 'party', 'get_election_type'
    )
    autocomplete_fields = ['race', 'division']
    inlines = [
        CandidateElectionInline
    ]

    def election_date(self, obj):
        return obj.election_day.date

    def get_election_type(self, obj):
        return obj.election_type.label

    get_election_type.short_description = 'Election Type'
