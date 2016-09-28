from haystack.forms import SearchForm


class SimpleSearchForm(SearchForm):
    def search(self):
        sqs = super(SimpleSearchForm, self).search()
        if not self.is_valid():
            return self.no_query_found()

        if not self.cleaned_data.get('q'):
            return self.no_query_found()

        if self.load_all:
            sqs = sqs.load_all()

        return sqs
