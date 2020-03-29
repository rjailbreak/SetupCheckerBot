import praw
import time


username = ''
password = ''
admin = ''
mods = ['']
clientid = ''
clientsecret = ''
version = ''
userAgent = ''
subreddit = ''
footer = '\n\n---\n\n*bleep bloop I\'m a bot*\n\nIf you have a specific question, you won\'t get an answer by PMming me. I only check setup posts. Please direct questions to [the moderators of r/iOSthemes](https://www.reddit.com/message/compose?to=%2Fr%2FiOSthemes).'
removalPM = 'Hello! Thank you for posting a setup to r/iOSthemes. However, it has been removed as I was unable to find a top level comment (a direct reply to your post) from you in the post with a tweak list. For example, if you included them in the imgur album description, you can simply write "Tweaks/themes used in album description". \n\nOnce you\'ve left a top level comment, **you need to reply to this PM to get your post approved.** When replying, please DO NOT change the subject of this message or send a new PM.' + footer


def checkPosts():
	# Get the 50 newest posts in r/iOSthemes
	for submission in r.subreddit(subreddit).new(limit = 15):
		print('  Checking post ' + submission.id + ' by ' + submission.author.name)

		# Post needs to be older than 2 hours and less than 2.5, needs flair of Setup, and should not have been approved or removed by anyone
		if (2 <= (time.time()-submission.created_utc)/(60*60) < 2.25) & (submission.link_flair_text == 'Setup') & (submission.banned_by == None) & (submission.approved_by == None):
			print('    Checking [Setup]')
			# Look for a top level comment posted by the author
			authorReplied = False
			commentBody = ''
			for comment in list(submission.comments):
				if submission.author == comment.author:
					print('    TLC found!')
					authorReplied = True
					commentBody = comment.body
					break

			# The comment contains the words "tweak" and matches: "tweaks", "tweaklist" etc. then approve.
			if authorReplied and ("tweak".lower() in commentBody.lower()):
				submission.mod.approve()
			# The TLC is too short, so we report it for further review
			elif (authorReplied) & (len(commentBody) < 100):
				submission.report(reason = 'OP\'s top level comment is short, please review')
			# The TLC is long enough, so approve it
			elif authorReplied:
				submission.mod.approve()
			# There is no TLC, so remove it
			else:
				if submission.is_self == False:
					print('    No TLC :(')
					submission.mod.remove()
					r.redditor(submission.author.name).message('Setup Post Removed - ' + submission.id, removalPM)
				else:
					submission.report(reason = 'Setup is a self post, please review')

		time.sleep(2)

def checkInbox():
	# Get the unread messages in the inbox
	for message in r.inbox.unread(limit = None):
		print('  Message from ' + message.author.name)

		# Make sure the message is a reply to one that SCB started
		if 're: Setup Post Removed - ' in message.subject:
			if ((time.time() - r.inbox.message(message.first_message_name[3:]).created_utc)/(60*60) > 4):
				response = 'Sorry, you took too long to reply to my PM and/or post a top level comment. A moderator will manually look into your post and approve it.'
				post = r.submission(id = message.subject[25:])
				post.report(reason = "OP took too long to respond. Please review.")
			else:
				print('    Looking for TLC')
				postID = message.subject[25:]
				post = r.submission(id = postID)
				# Look for a TLC from OP
				if post.id == postID:
					authorReplied = False
					for comment in list(post.comments):
						if message.author == comment.author:
							authorReplied = True
							commentBody = comment.body
							com = comment
							break
							
				# The comment contains the words "tweak" and matches: "tweaks", "tweaklist" etc. then approve.
				if (authorReplied) & "tweak".lower() in commentBody.lower():
					submission.mod.approve()
				# The TLC is too short, so we report it for further review
				elif (authorReplied) & (len(commentBody) < 100):
					submission.report(reason = 'OP\'s top level comment is short, please review')
				# The TLC is long enough, so approve it
				elif authorReplied:
					submission.mod.approve()
				# Ask them to try again if not
				else:
					print('    Nope :(')
					response = 'Sorry, I wasn\'t able to find a top level comment from you. Be sure that you are replying directly to your OWN POST, not to someone who replied to your post.'

			response += footer
			message.reply(response)
		elif (message.subject == 'username mention') & (message.author.name in mods):
			print('    Mention from r/iOSthemes mod')
			post = r.submission(id=message.parent_id[3:])
			if post.link_flair_text == 'Setup':
				if message.body.lower() == 'u/setupcheckerbot remove':
					post.mod.remove()
					message.mod.remove()
					r.redditor(post.author.name).message('Setup Post Removed - ' + post.id, removalPM)
		else:
			print('    Forward to admin')
			r.redditor(admin).message('FWD "' + message.subject + '" from u/' + message.author.name, message.body)

		message.mark_read()
		time.sleep(2)

def checkSent():
	for message in r.inbox.sent(limit = 10):
		print('  PM to u/' + message.dest.name)

		# Look for PMs to users, not to the admin
		if ('Setup Post Removed' in message.subject) & (message.dest.name is not admin):
			# If the PM is a "root" PM
			if (message.first_message == None) & (4 < (time.time() - message.created_utc)/(60*60) < 4.25):
				print('    Verifying TLC')
				verified = False
				# Check the replies to the root PM
				for m in list(r.inbox.message(message.id).replies):
					print('  Good')

					# If one of the replies is SCB approving a post, then we good
					if ('Thanks! Your setup post has been approved' in m.body) & (message.author == m.author):
						verified = True

				# Before banning, do one more check for a TLC
				if not verified:
					postID = message.subject[21:]
					post = r.submission(id = postID)
					if post.id == postID:
						for comment in list(post.comments):
							if message.dest == comment.author:
								post.mod.approve()
								verified = True

		else:
			print('    Message to admin, skipping')

		time.sleep(2)

if __name__ == '__main__':
	r = praw.Reddit(client_id = clientid, client_secret = clientsecret, user_agent = userAgent, username = username, password = password)

	# Review the setup posts
	print('Checking New Posts')
	checkPosts()

	# Check the inbox
	print('Checking Inbox')
	checkInbox()

	# Check sent messages
	print('Checking Sent Messages')
	checkSent()
