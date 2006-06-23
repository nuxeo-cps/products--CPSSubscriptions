##parameters=
#$Id$
""" Mail Template fr

pour utiliser ce template il faut le renommer getMailTemplate.py dans
une de vos skin
"""

mail_subject = "[%(portal_title)s] %(notification_title)s sur le é document %(object_title)s"
mail_body = \
"""%(user_name)s (%(user_id)s) a effectué un(e) %(notification_title)s
sur le document %(object_title)s.

Ce document est disponible à l'adresse suivante :
    %(object_url)s

Commentaires : %(comments)s
"""

mail_error_body = \
"""Une erreur s'est produite lors de la génération automatique de ce message.

Veuillez contacter votre admistrateur pour plus d'informations.
"""

subscribe_confirm_email_title = \
"""[%(portal_title)s] Confirmation d'abonnement
"""
subscribe_confirm_email_body = \
"""Confirmation d'abonnement à la liste de diffusion: %(event_id)s

Nous avaons reçu une demande d'abonnement pour votre adresse email,
%(email)s, pour la liste %(event_id)s.

Vous devez confimer votre abonnement sur la page:

%(object_url)s
"""

subscribe_welcome_email_title = \
"""[%(portal_title)s] Bienvenue sur la liste de diffusion %(object_title)s
"""

subscribe_welcome_email_body = \
"""Bienvenue sur la liste %(event_id)s accessible depuis :

%(object_url)s

Pour plus d'information ou vous désabonner de la liste :

%(info_url)s
"""

unsubscribe_email_title = \
"""[%(portal_title)s] Désabonnement
"""

unsubscribe_email_body = \
"""Vous êtes désabonné de la liste de diffusion %(object_title)s at %(object_url)s
"""

unsubscribe_confirm_email_title = \
"""[%(portal_title)s] Confirmation de désabonnement
"""

unsubscribe_confirm_email_body = \
"""Vous avez demandé à vous désabonner de la liste de diffusion :

%(object_title)s à :

%(object_url)s

Aller sur la page suivante pour confirmer :

%(url)s
"""

template = {}
template['mail_subject'] = mail_subject
template['mail_body'] = mail_body
template['mail_error_body'] = mail_error_body
template['subscribe_confirm_email_title'] = subscribe_confirm_email_title
template['subscribe_confirm_email_body'] = subscribe_confirm_email_body
template['subscribe_welcome_email_title'] = subscribe_welcome_email_title
template['subscribe_welcome_email_body'] = subscribe_welcome_email_body
template['unsubscribe_email_title'] = unsubscribe_email_title
template['unsubscribe_email_body'] = unsubscribe_email_body
template['unsubscribe_confirm_email_title'] = unsubscribe_confirm_email_title
template['unsubscribe_confirm_email_body'] = unsubscribe_confirm_email_body

return template
