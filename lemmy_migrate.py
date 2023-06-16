from lemmy import Lemmy

lemming = Lemmy('https://sh.itjust.works')
lemming.login()
communties = lemming.get_communities()

new_lemming = Lemmy('https://infosec.pub')
new_lemming.login()
new_lemming.subscribe(communties)
