bump:
	bumpver update --patch --no-fetch

bump_minor:
	bumpver update minor --no-fetch

bump_major:
	bumpver update major --no-fetch

bump_beta:
	bumpver update --no-fetch --patch --tag=beta --tag-num

bump_dev:
	bumpver update --no-fetch --patch --tag=dev --tag-num

bump_next_pre:
	bumpver update --no-fetch --tag-num

bump_final:
	bumpver update --no-fetch --tag=final
