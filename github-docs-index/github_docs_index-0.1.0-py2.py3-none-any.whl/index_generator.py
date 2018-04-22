"""
The latest version of this package is available at:
<http://github.com/jantman/github-docs-index>

##################################################################################
Copyright 2018 Jason Antman <jason@jasonantman.com> <http://www.jasonantman.com>

    This file is part of github-docs-index, also known as github-docs-index.

    github-docs-index is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    github-docs-index is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with github-docs-index.  If not, see <http://www.gnu.org/licenses/>.

The Copyright and Authors attributions contained herein may not be removed or
otherwise altered, except to add the Author attribution of a contributor to
this work. (Additional Terms pursuant to Section 7b of the AGPL v3)
##################################################################################
While not legally required, I sincerely request that anyone who finds
bugs please submit them at <https://github.com/jantman/github-docs-index> or
to me via email, and that you send any contributions or improvements
either as a pull request on GitHub, or to me via email.
##################################################################################

AUTHORS:
Jason Antman <jason@jasonantman.com> <http://www.jasonantman.com>
##################################################################################
"""

from github_docs_index.index_document import IndexDocument


class GithubDocsIndexGenerator(object):

    def __init__(self, config):
        self._conf = config
        self._links = []

    def generate_index(self, additional_links=[]):
        """
        Main entry point to query GitHub, retrieve repository information,
        generate the index document and return rST.

        :param additional_links: Optional list of additional
          :py:class:`~.IndexLink` instances to include in the documentation
          index.
        :type additional_links: ``list`` of :py:class:`~.IndexLink`
        :returns: generated rST index document
        """
        doc = IndexDocument(self._conf)
        for gh in self._conf.githubs:
            doc.add_indexlinks(gh.get_docs_repos())
        doc.add_indexlinks(additional_links)
        return doc.generate_rst()
