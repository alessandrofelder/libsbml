#!/usr/bin/env python
##
## @file    rewrite_pydoc.py
## @brief   Convert libSBML Python doc file to something usable for doc strings
## @author  Mike Hucka
## 
## <!--------------------------------------------------------------------------
## This file is part of libSBML.  Please visit http://sbml.org for more
## information about SBML, and the latest version of libSBML.
##
## Copyright (C) 2009-2012 jointly by the following organizations: 
##     1. California Institute of Technology, Pasadena, CA, USA
##     2. EMBL European Bioinformatics Institute (EBML-EBI), Hinxton, UK
##  
## Copyright (C) 2006-2008 by the California Institute of Technology,
##     Pasadena, CA, USA 
##  
## Copyright (C) 2002-2005 jointly by the following organizations: 
##     1. California Institute of Technology, Pasadena, CA, USA
##     2. Japan Science and Technology Agency, Japan
## 
## This library is free software; you can redistribute it and/or modify it
## under the terms of the GNU Lesser General Public License as published by
## the Free Software Foundation.  A copy of the license agreement is provided
## in the file named "LICENSE.txt" included with this software distribution
## and also available online as http://sbml.org/software/libsbml/license.html
## ------------------------------------------------------------------------ -->

import argparse
import re
import sys
import os
import textwrap
from htmllib import HTMLParser
from formatter import NullWriter, AbstractFormatter


# -----------------------------------------------------------------------------
# Command-line argument handling.
# -----------------------------------------------------------------------------

__desc = '''Translates the libSBML Doxygen help text in file "pydoc.i" 
into a form suitable to serve as Python help strings.'''

__desc_end = '''This file is part of libSBML.  Please visit http://sbml.org for
more information about SBML, and the latest version of libSBML.'''


def parse_cmdline(direct_args = None):
    parser = argparse.ArgumentParser(description=__desc, epilog=__desc_end)
    parser.add_argument("-q", "--quiet", action="store_const", const=True,
                        help="be quiet -- don't print messages")
    parser.add_argument("-f", "--file", required=True,
                        help="specify the file to translate")
    parser.add_argument("-o", "--output", required=True,
                        help="specify the file to store the results")
    parser.add_argument("-i", "--include",
                        help="specify the directory for @htmlinclude files")
    parser.add_argument("-g", "--graphics",
                        help="specify the directory for @image files")
    return parser.parse_args(direct_args)


def get_input_file_name(direct_args = None):
    return expanded_path(direct_args.file)


def get_output_file_name(direct_args = None):
    return expanded_path(direct_args.output)


def get_include_dir(direct_args = None):
    return expanded_path(direct_args.include)


def get_graphics_dir(direct_args = None):
    return expanded_path(direct_args.graphics)


def get_quiet_flag(direct_args = None):
    return direct_args.quiet


# -----------------------------------------------------------------------------
# Helper classes.
# -----------------------------------------------------------------------------

# This is a modifid version of DumbWriter from Python 2.6's formatter.py.  The
# original DumbWriter is hardwired to write its output to a file; this version
# writes all text to an internal string variable.  The contents can be
# obtained using a call to get_text().

class RewritePydocStringWriter(NullWriter):

    def __init__(self, maxcol=72):
        self.text = ''
        self.maxcol = maxcol
        NullWriter.__init__(self)
        self.reset()

    def reset(self):
        self.col = 0
        self.atbreak = 0

    def send_paragraph(self, blankline):
        self.text += '\n'*blankline
        self.col = 0
        self.atbreak = 0

    def send_line_break(self):
        self.text += '\n'
        self.col = 0
        self.atbreak = 0

    def send_hor_rule(self, *args, **kw):
        self.text += '\n' + '-'*self.maxcol + '\n'
        self.col = 0
        self.atbreak = 0

    def send_literal_data(self, data):
        self.text += data
        i = data.rfind('\n')
        if i >= 0:
            self.col = 0
            data = data[i+1:]
        data = data.expandtabs()
        self.col = self.col + len(data)
        self.atbreak = 0

    def send_flowing_data(self, data):
        if not data: return
        atbreak = self.atbreak or data[0].isspace()
        col = self.col
        maxcol = self.maxcol
        for word in data.split():
            if atbreak:
                if col + len(word) >= maxcol:
                    self.text += '\n'
                    col = 0
                else:
                    self.text += ' '
                    col = col + 1
            self.text += word
            col = col + len(word)
            atbreak = 1
        self.col = col
        self.atbreak = data[-1].isspace()

    def get_text(self):
        return latin1_to_ascii(self.text)


# This is derived from Python 2.6's htmllib HTMLParser class, with the only
# difference that it doesn't add an anchor like "[1]" into the text it
# writes when it encounters a <a ...>...</a> element in the HTML input.

class RewritePydocHTMLParser(HTMLParser):

    def anchor_end(self):
        pass


# -----------------------------------------------------------------------------
# Body
# -----------------------------------------------------------------------------

def expanded_path(path):
    if path: return os.path.expanduser(os.path.expandvars(path))
    else:    return None


def read_file_contents(file):
    istream  = open(file, 'r')
    contents = istream.read()
    istream.close()
    return contents


def write_output_file(file, contents):
    output = open(file, 'w')
    output.write(contents)
    output.close()


def valid_file(file, quiet=False):
    if not os.path.exists(file):
        return False
    elif not os.path.isfile(file):
        return False
    else:
        return True


def valid_directory(dir, quiet=False):
    if not os.path.exists(dir):
        return False
    elif not os.path.isdir(dir):
        return False
    else:
        return True
    

# The following came from a StackOverflow posting by "Soldier.moth" in 2011:
# http://stackoverflow.com/questions/930303/python-string-cleanup-manipulation-accented-characters

def latin1_to_ascii (unicrap):
    """This replaces UNICODE Latin-1 characters with
    something equivalent in 7-bit ASCII. All characters in the standard
    7-bit ASCII range are preserved. In the 8th bit range all the Latin-1
    accented letters are stripped of their accents. Most symbol characters
    are converted to something meaningful. Anything not converted is deleted.
    """
    xlate = {
        0xc0:'A', 0xc1:'A', 0xc2:'A', 0xc3:'A', 0xc4:'A', 0xc5:'A',
        0xc6:'Ae', 0xc7:'C', 0xc8:'E', 0xc9:'E', 0xca:'E', 0xcb:'E',
        0xcc:'I', 0xcd:'I', 0xce:'I', 0xcf:'I', 0xd0:'Th', 0xd1:'N',
        0xd2:'O', 0xd3:'O', 0xd4:'O', 0xd5:'O', 0xd6:'O', 0xd8:'O',
        0xd9:'U', 0xda:'U', 0xdb:'U', 0xdc:'U', 0xdd:'Y', 0xde:'th',
        0xdf:'ss', 0xe0:'a', 0xe1:'a', 0xe2:'a', 0xe3:'a', 0xe4:'a',
        0xe5:'a', 0xe6:'ae', 0xe7:'c', 0xe8:'e', 0xe9:'e', 0xea:'e',
        0xeb:'e', 0xec:'i', 0xed:'i', 0xee:'i', 0xef:'i', 0xf0:'th',
        0xf1:'n', 0xf2:'o', 0xf3:'o', 0xf4:'o', 0xf5:'o', 0xf6:'o',
        0xf8:'o', 0xf9:'u', 0xfa:'u', 0xfb:'u', 0xfc:'u', 0xfd:'y',
        0xfe:'th', 0xff:'y', 0xa0: ' ', 0xa1:'!', 0xa2:'{cent}',
        0xa3:'{pound}', 0xa4:'{currency}', 0xa5:'{yen}', 0xa6:'|',
        0xa7:'{section}', 0xa8:'{umlaut}', 0xa9:'{C}', 0xaa:'{^a}',
        0xab:'<<', 0xac:'{not}', 0xad:'-', 0xae:'{R}', 0xaf:'_',
        0xb0:'{degrees}', 0xb1:'{+/-}', 0xb2:'{^2}', 0xb3:'{^3}', 0xb4:"'",
        0xb5:'{micro}', 0xb6:'{paragraph}', 0xb7:'*', 0xb8:'{cedilla}',
        0xb9:'{^1}', 0xba:'{^o}', 0xbb:'>>', 0xbc:'{1/4}', 0xbd:'{1/2}',
        0xbe:'{3/4}', 0xbf:'?', 0xd7:'*', 0xf7:'/'
        }

    r = ''
    for i in unicrap:
        if xlate.has_key(ord(i)):
            r += xlate[ord(i)]
        elif ord(i) >= 0x80:
            pass
        else:
            r += i
    return r


def rewrite(contents, include_dir, graphics_dir, quietly):
    p = re.compile('(%feature\("docstring"\) \S+ "\n)(.*?)(^";\n\s*)', re.DOTALL|re.MULTILINE)
    return p.sub(lambda text: rewrite_each(text, include_dir, graphics_dir, quietly), contents)


def rewrite_each(match, include_dir, graphics_dir, quietly):
    feature_line = match.group(1)
    doc_body     = match.group(2)
    tail         = match.group(3)

    if re.search('@internal', doc_body):   # Skip everything if it's internal.
        doc_body = " Internal implementation method.\n"
    else:        
        doc_body = rewrite_one_body(doc_body, include_dir, graphics_dir, quietly)
    return feature_line + doc_body + tail


def rewrite_one_body(body, include_dir, graphics_dir, quietly):
    # First, some configurable values, to help improve consistency.

    line_width  = 70
    list_indent = 3

    # Start by removing ^M characters, because they confuse the
    # interpretation of ends of lines.  (They shouldn't be in the input
    # file in the first place, but Windows users using svn sometimes
    # introduce them by accident.)

    body = re.sub(r'\015', '', body)

    # Next, deal with conditionals, since that affects what else needs to
    # be done.

    p = re.compile(r'@if\s+(\S+)\s+(.+?)((@else)\s+(.+?))?@endif', re.DOTALL)
    body = p.sub(rewrite_if_else, body)

    # Insert inclusions.

    p = re.compile(r'@htmlinclude\s+([^\s:;,(){}+|?"\'/]+)([\s:;,(){}+|?"\'/])')
    body = p.sub(lambda match: rewrite_htmlinclude(match, include_dir, quietly), body)

    # Do basic HTML entities.  These can show up in verbatim blocks, so we
    # do them before processing verbatim blocks.

    body = re.sub(r'&lt;',       '<',        body)
    body = re.sub(r'&gt;',       '>',        body)
    body = re.sub(r'&#34;',      '\\"',      body)
    body = re.sub(r'&#64;',      '@',        body)
    body = re.sub(r'&quot;',     '\\\\"',    body)

    # Remove & store verbatim blocks.  These present a special challenge
    # because we don't want to fill the paragraphs in these regions.  The
    # approach here is to store the blocks and put them back in a final
    # step at the end.  Note that verbatim, code and <pre> are all formatted
    # in the same way, because in plain-text it's difficult to make the
    # distinctions clear (and anyway, we don't use them much differently
    # in the libSBML code).

    verbatim_blocks = []
    p = re.compile('@verbatim(.+?)@endverbatim\n', re.DOTALL)
    body = p.sub(lambda match: record_placeholder(match, verbatim_blocks), body)
    p = re.compile('@code(.+?)@endcode\n', re.DOTALL)
    body = p.sub(lambda match: record_placeholder(match, verbatim_blocks), body)

    # Treat the signature descriptions (which also use <pre>) differently:
    p = re.compile(r"<pre class='signature'>(.+?)</pre>", re.DOTALL|re.IGNORECASE)
    body = p.sub(r"\n    \1\n", body)
    p = re.compile(r"<pre.*?>(.+?)</pre>", re.DOTALL|re.IGNORECASE)
    body = p.sub(lambda match: record_placeholder(match, verbatim_blocks), body)

    # Do other HTML constructs.

    p = re.compile(r'<!--(.+?) -->', re.DOTALL) # HTML comments get removed.
    body = p.sub(r'', body)

    body = re.sub(r'&nbsp;',     ' ',                           body)
    body = re.sub(r'&ndash;',    '-',                           body)
    body = re.sub(r'&mdash;',    ' -- ',                        body)
    body = re.sub(r'</?[bpi]>',  '',                            body)
    body = re.sub(r'<br>',       '\n',                          body)
    body = re.sub(r'<ul>',       '\n',                          body)
    body = re.sub(r'</ul>',      '',                            body)
    body = re.sub(r'<li.*?>',    '\n' + ' '*list_indent + '* ', body)

    p = re.compile(r'<code>(.+?)</code>', re.DOTALL|re.IGNORECASE)
    body = p.sub(r'\1', body)

    p = re.compile(r'<span.*?>(.+?)</span>', re.DOTALL|re.IGNORECASE)
    body = p.sub(r'\1', body)

    p = re.compile(r'<sub>(.+?)</sub>', re.DOTALL|re.IGNORECASE)
    body = p.sub(r'_\1', body)

    p = re.compile(r'<sup>\s*(.+?)\s*</sup>', re.DOTALL|re.IGNORECASE)
    body = p.sub(r'^\1', body)

    p = re.compile(r'<em>(.+?)</em>', re.DOTALL|re.IGNORECASE)
    body = p.sub(r'\1', body)

    p = re.compile(r'<a.+?>(.+?)</a>', re.DOTALL|re.IGNORECASE)
    body = p.sub(r'\1', body)

    # Next, rewrite most Doxygen tags.

    body = rewrite_see(body)

    body = re.sub(r'%',          '',                            body)
    body = re.sub(r'@li\s+',     '\n' + ' '*list_indent + '* ', body)
    body = re.sub(r'@em\s+',     '',                            body)
    body = re.sub(r'@return\s+', 'Returns ',                    body)

    p = re.compile(r'@c\s+(\S+(\(\))?)', re.IGNORECASE)
    body = p.sub(r'\1', body)

    p = re.compile(r'@param\s+(\S+)\s+', re.IGNORECASE)
    body = p.sub(r'Parameter \'\1\' is ', body)

    p = re.compile(r'@throws\s+(\S+)\s+', re.IGNORECASE)
    body = p.sub(r'Throws \1: ', body)

    p = re.compile(r'@deprecated\s+(\S+)\s+', re.IGNORECASE)
    body = p.sub(r'DEPRECATED. \1 ', body)

    p = re.compile(r'@p\s+(\S+)\b', re.IGNORECASE)
    body = p.sub(r"'\1'", body)

    p = re.compile(r'@link\s+(\S+)(\s+\S+\s*)?@endlink', re.IGNORECASE)
    body = p.sub(r'\1', body)

    p = re.compile(r'@note(\s*)', re.IGNORECASE)
    body = p.sub(r'Note:\n\n\1', body)    

    p = re.compile(r'@docnote(\s*)', re.IGNORECASE)
    body = p.sub(r'Documentation note:\n\n\1', body)    

    p = re.compile(r'@warning(\s*)', re.IGNORECASE)
    body = p.sub(r'WARNING:\n\n\1', body)    

    # Handle @image as best as we can.  We ignore @image latex, and for
    # @image html, we will try to substitute a .txt file later on.

    body = re.sub(r'@image\s+latex.+?\n', '', body, re.IGNORECASE)

    # Miscellaneous other adjustments.

    body = re.sub(r"\\'", "'", body)      # Don't need quoted single quotes.

    # Remove excess inter-paragraph spacing prior to rewrapping paragraphs,
    # or the extra spaces at the beginning of blank lines can introduce
    # extra leading spaces in the first lines of the paragraphs.

    body = re.sub(r'\n *\n *\n *', '\n\n ', body)

    # Wrap paragraphs, so that the text is more readable.

    p = re.compile(r'(.+?)(\n *\n|\Z)', re.DOTALL)
    body = p.sub(lambda match: rewrite_fill_paragraph(match, line_width), body)

    # Handle "@image html".  Do this after wrapping, or else the contents of
    # what we insert will end up wrapped.

    p = re.compile(r'@image\s+html\s+(\S+).*?(\n *\n)', re.DOTALL)
    body = p.sub(lambda match: rewrite_image(match, graphics_dir, quietly), body)

    # Handle @section and other headings, adding underlining to them.  Also
    # handle <hr> tags.  This all needs to be done last, after filling
    # paragraphs.

    p = re.compile(r'^ *<hr> ?', re.MULTILINE)
    body = p.sub(' ' + '_'*line_width + '\n', body)
    p = re.compile(r'@(sub)?section\s+\S+\s+(.+?)(\n *\n)', re.DOTALL|re.IGNORECASE)
    body = p.sub(lambda match: rewrite_section_heading(match, line_width), body)
    p = re.compile(r'(<h3>)\s*(.+?)</h3>(\n *\n)', re.DOTALL|re.IGNORECASE)
    body = p.sub(lambda match: rewrite_section_heading(match, line_width), body)

    # Finally, replace verbatim block placeholders and format them.

    p = re.compile(r'{{{{(\d+)}}}}')
    body = p.sub(lambda match: rewrite_verbatim(match, verbatim_blocks, line_width), body)

    # Remove excess inter-paragraph spacing one more time, to normalize
    # spacing above and below verbatim's.

    body = re.sub(r'\n *\n *\n', '\n\n ', body)

    # And we're done.

    return ' ' + body.strip() + '\n'


def rewrite_if_else(match):
    lang = match.group(1)
    if lang == 'python' or lang == 'notcpp' or lang == 'notclike':
        return match.group(2)
    elif match.group(4) == '@else':
        return match.group(5)
    else:
        return ''


def record_placeholder(match, placeholder_list):
    text = match.group(1)    
    placeholder_list.append(text)
    index = len(placeholder_list) - 1
    return '\n{{{{' + str(index) + '}}}}\n'


def rewrite_verbatim(match, placeholder_list, line_width):
    index = int(match.group(1))
    text = placeholder_list[index]
    text = re.sub(r'\n', '\n    ', text).strip()
    body = '\n' + '    ' + text + '\n'
    return body


def rewrite_see(text):
    matches = []
    words = []
    for m in re.finditer(r'(@see\s+(\S+)(\s+const)?[ \t]*\n)+', text):
        matches.append(m)
        words.append(m.group(2))

    if len(matches) == 0: return text

    pre_text         = text[:matches[0].start(0)]
    replacement_text = 'See also ' + ', '.join(words) + '.\n'
    post_text        = text[matches[-1].end(0):]

    return pre_text + replacement_text + post_text


def rewrite_section_heading(match, line_width):
    is_subsection   = (match.group(1) != None)
    heading_text    = match.group(2)
    tail_whitespace = match.group(3)
    if is_subsection:
        underline_char = '.'
    else:
        underline_char = '='
    heading_text = wrap_paragraph(heading_text, line_width).strip()
    return heading_text + "\n " + underline_char*70 + tail_whitespace


def rewrite_htmlinclude(match, include_dir, quietly):
    file_path = os.path.join(include_dir, match.group(1))    
    trailing_char = match.group(2)

    if not valid_file(file_path):
        if not quietly:
            print "Warning: unable to expand @htmlinclude '" + match.group(1) + "'"
        return ''

    # First, try to see if there's a .txt version.  If so, use that.

    txt_file = re.sub(r'html', 'txt', file_path, re.IGNORECASE)
    if valid_file(txt_file):
        file = open(txt_file, 'r')
        contents = file.read()
        file.close()
        contents = re.sub('\n', '\n ', contents) # Indent ever line.
        contents = re.sub(r'"', '\\"', contents) # Quote all double quotes.
        return contents + trailing_char
    else:                               # No txt file; proceed with .html file.
        file = open(file_path, 'r')

        writer = RewritePydocStringWriter()
        parser = RewritePydocHTMLParser(AbstractFormatter(writer))
        parser.feed(file.read())
        parser.close()
        file.close()

        text = writer.get_text()
        text = re.sub(r'\n', '\n ', text)   # Add leading space to every line.
        text = re.sub(r'"', '\\"', text)    # Quote all double quotes.
        text += trailing_char

        return text


def rewrite_image(match, graphics_dir, quietly):
    file_name      = match.group(1)
    txt_file       = re.sub(r'jpg', 'txt', file_name, re.IGNORECASE)
    file_path      = os.path.join(graphics_dir, txt_file)
    trailing_space = match.group(2)

    if not valid_file(file_path):
        if not quietly:
            print "Warning: unable to open @image txt file for '" + file_name + "'"
        return ''

    file = open(file_path, 'r')
    contents = file.read()
    file.close()
    contents = re.sub('\n', '\n ', contents) # Indent every line.
    contents = re.sub(r'"', '\\"', contents) # Quote all double quotes.

    return contents + trailing_space


def rewrite_fill_paragraph(match, line_width):
    text = match.group(1)
    return wrap_paragraph(text, line_width)


def wrap_paragraph(text, line_width):
    return textwrap.fill(text, subsequent_indent = ' ', width = line_width) + '\n\n'


def main():
    args         = parse_cmdline()
    input_file   = get_input_file_name(args)
    output_file  = get_output_file_name(args)
    include_dir  = get_include_dir(args)
    graphics_dir = get_graphics_dir(args)
    quietly      = get_quiet_flag(args)

    # Sanity-check the arguments.

    if not valid_file(input_file, quietly):
        if not quietly:
            if not quietly: print "Error: cannot read file '" + input_file + "'"
        sys.exit(1)
    elif include_dir and not valid_directory(include_dir, quietly):
        if not quietly:
            if not quietly: print "Error: cannot access directory '" + input_file + "'"
        sys.exit(1)
    elif graphics_dir and not valid_directory(graphics_dir, quietly):
        if not quietly:
            if not quietly: print "Error: cannot access directory '" + input_file + "'"
        sys.exit(1)

    # Let's do this thing.

    results = rewrite(read_file_contents(input_file), include_dir,
                      graphics_dir, quietly)
    write_output_file(output_file, results)


if __name__ == '__main__':
  main()

