from core.views import Change

class Flow(Change):
    template_name = 'core/flow.html'

    def get(self, request, pk):
        self.kwargs['app'] = 'core'
        self.kwargs['model'] = 'flow'
        return super().get(request, 'core', 'flow', pk)
    
    def post(self, request, pk):
        self.kwargs['app'] = 'core'
        self.kwargs['model'] = 'flow'
        return super().post(request, 'core', 'flow', pk)