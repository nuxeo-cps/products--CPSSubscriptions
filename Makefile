check:
	pychecker2 *.py

clean:
	find . -name '*~' | xargs rm -f
	find . -name '*.pyc' | xargs rm -f
	find . -name '#*' | xargs rm -f
	#rm -rf doc/API
	cd tests ; make clean

docs:
	happydoc -d doc/API *.py
