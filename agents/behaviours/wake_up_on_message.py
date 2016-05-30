import spade


class WakeUpOnMessage(spade.Behaviour.EventBehaviour):
    def _process(self):
        print "This behaviour has been triggered by a message!"

        self.msg = self._receive(False)
        if self.msg:
            print self.msg.getContent()