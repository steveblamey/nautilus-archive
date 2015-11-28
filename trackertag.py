"""A simple wrapper for Tracker SPARQL queries and updates related to file tagging.
"""
import gi
gi.require_version('Tracker', '1.0')

from gi.repository import Tracker


class TrackerTag():
    def __init__(self):
        self.connection = Tracker.SparqlConnection.get(None)

    def tag_exists(self, tag_label):
        """Check if a tag already exists in the tracker DB"""
        if self.connection:
            squery = "SELECT ?tag WHERE { ?tag a nao:Tag . ?tag nao:prefLabel '%s' }" % tag_label
            cursor = self.connection.query(squery, None)
            while(cursor.next(None)):
                if cursor.get_string(0):
                    return True
                else:
                    return False
        else:
            raise Exception("Couldn't get a proper SPARQL connection")
            return False

    def new_tag(self, tag_label):
        """Create a new tag in the tracker DB"""
        if self.connection:
            uquery = ("INSERT { _:tag a nao:Tag ; nao:prefLabel '%s' .}"
                      "WHERE { OPTIONAL { ?tag a nao:Tag ; nao:prefLabel '%s' } ."
                      "FILTER (!bound(?tag)) }") % (tag_label, tag_label)
            cursor = self.connection.update(uquery, 1, None)
            return True
        else:
            raise Exception("Couldn't get a proper SPARQL connection")
            return False

    def add_tag(self, uri, tag_label):
        if self.connection:
            uquery = ("INSERT { ?urn nao:hasTag ?label }"
                      "WHERE { ?urn nie:url '%s' ."
                      "?label nao:prefLabel '%s' }") % (uri, tag_label)
            cursor = self.connection.update(uquery, 1, None)
            return True
        else:
            raise Exception("Couldn't get a proper SPARQL connection")
            return False

    def remove_tag(self, uri, tag_label):
        if self.connection:
            uquery = ("DELETE { ?urn nao:hasTag ?label }"
                      "WHERE { ?urn nie:url '%s' ."
                      "?label nao:prefLabel '%s' }") % (uri, tag_label)
            cursor = self.connection.update(uquery, 1, None)
            return True
        else:
            raise Exception("Couldn't get a proper SPARQL connection")
            return False

    def has_tag(self, uri, tag_label):
        if self.connection:
            squery = "SELECT ?f WHERE { ?f nie:url '%s' ; nao:hasTag [ nao:prefLabel '%s' ]}" % (uri, tag_label)
            cursor = self.connection.query(squery, None)
            while(cursor.next(None)):
                if cursor.get_string(0):
                    return True
                else:
                    return False
        else:
            raise Exception("Couldn't get a proper SPARQL connection")
            return False

    def get_tags(self, uri):
        """Return all tags for a file uri

        Arguments:
        uri -- a file uri, e.g. 'file:///home/user/file.txt'

        Returns:
        A list of tags or False if the file has no tags
        """
        if self.connection:
            squery = ("SELECT ?labels WHERE { ?f nie:isStoredAs ?as ; nao:hasTag ?tags . ?as nie:url '%s' ."
                      "?tags a nao:Tag ; nao:prefLabel ?labels .}") % uri
            cursor = self.connection.query(squery, None)
            tag_list = []
            while(cursor.next(None)):
                tag_list.append(cursor.get_string(0))
            if len(tag_list) != 0:
                    return tag_list
            else:
                return False
        else:
            raise Exception("Couldn't get a proper SPARQL connection")
            return False

    def tagged_files(self, tag_labels):
        """Return uris with a tag or tags

        Arguments:
        tag_labels -- either a string value representing a tag, e.g. 'tag' or a tuple, ('thistag', 'thattag')

        Returns:
        A list of file uris or False if no files match.
        """
        if self.connection:
            if isinstance(tag_labels, tuple):
                labels = repr(tuple(map(str, tag_labels)))
                squery = ("SELECT DISTINCT ?urn nie:url(?urn)"
                          "WHERE { ?urn nao:hasTag [ nao:prefLabel ?label ] ."
                          "FILTER(?label IN %s) .}") % labels
            else:
                squery = ("SELECT ?urn nie:url(?urn)"
                          "WHERE { ?urn nao:hasTag [ nao:prefLabel '%s' ]}") % tag_labels

            cursor = self.connection.query(squery, None)
            uri_list = []
            while (cursor.next(None)):
                uri_list.append(cursor.get_string(1)[0])
            if len(uri_list) != 0:
                return uri_list
            else:
                return False
        else:
            raise Exception("Couldn't get a proper SPARQL connection")
            return False
