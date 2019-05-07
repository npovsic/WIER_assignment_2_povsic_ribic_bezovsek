from bs4 import BeautifulSoup


class RoadRunner:
    def __init__(self, sites_to_parse):
        self.sites_to_parse = sites_to_parse

        self.output = {
            'pages': []
        }

    def start(self):
        for site in self.sites_to_parse:
            page1 = site["pages"][0]
            soup1 = BeautifulSoup(page1, 'lxml')
            tree1 = self.build_dom_tree(soup1.find("html"))

            page2 = site["pages"][1]
            soup2 = BeautifulSoup(page2, 'lxml')
            tree2 = self.build_dom_tree(soup2.find("html"))

            generalized_tree = self.build_generalized_tree(tree1, tree2)

            with open('output/roadrunner_{}.txt'.format(site["type"]), 'w') as file:
                file.write(self.create_regex(generalized_tree))

    def build_dom_tree(self, soup):
        return None if soup.name is None else {"tag": soup.name,
                                               "id": soup.id if soup.id else "",
                                               "class": soup.attrs['class'] if "class" in soup.attrs else [],
                                               "children": list(filter(None, [self.build_dom_tree(child) for child in
                                                                              soup.children])),
                                               "has_closing_tag": not soup.is_empty_element,
                                               "has_text": soup.string is not None}

    def set_as_optional(self, element):
        element["is_optional"] = True
        element["children"] = [self.set_as_optional(child) for child in element["children"]]
        return element

    def is_optional(self, element1, element2):
        return element1["tag"] != element2["tag"]

    def build_generalized_tree(self, tree1, tree2):
        if self.is_optional(tree1, tree2):
            tree1 = self.set_as_optional(tree1)

        else:
            if tree1["children"]:
                for index in range(min(len(tree1["children"]), len(tree2["children"]))):
                    tree1["children"][index] = self.build_generalized_tree(tree1["children"][index],
                                                                           tree2["children"][index])

                if len(tree1["children"]) > len(tree2["children"]):
                    for index in range(len(tree2["children"]), len(tree1["children"])):
                        tree1["children"][index] = self.set_as_optional(tree1["children"][index])
                else:
                    for index in range(len(tree1["children"]), len(tree2["children"])):
                        tree1["children"].append(self.set_as_optional(tree2["children"][index]))

            elif tree2["children"]:
                tree1["children"] = [self.set_as_optional(child) for child in tree2["children"]]

            else:
                return tree1

        return tree1

    def check_if_list(self, prev_element, next_element):
        if prev_element is None or next_element is None:
            return False

        if prev_element["tag"] != next_element["tag"]:
            return False

        if not prev_element["children"] and not next_element["children"]:
            return True

        if prev_element["children"] and not next_element["children"] \
                or not prev_element["children"] and next_element["children"]:
            return False

        for index in range(len(prev_element["children"])):
            is_list = False if index >= len(next_element["children"]) else self.check_if_list(
                prev_element["children"][index], next_element["children"][index])
            if not is_list:
                return False

        return True

    def mark_list_in_regex(self, regex, tag):
        if regex[len(regex) - 1] == "+":
            return regex

        if regex[len(regex) - 1] == "?":
            return regex[:len(regex) - 1] + "*"

        i = regex.rfind("<" + tag + ">")

        return regex[:i] + "(" + regex[i:] + ")+"

    def create_regex(self, generalized_tree):
        regex = ""

        is_optional = "is_optional" in generalized_tree and generalized_tree["is_optional"]

        if is_optional:
            regex += "("

        regex += "<" + generalized_tree["tag"] + ">"

        if generalized_tree["has_text"]:
            regex += "#text"

        prev_element = None

        for child in generalized_tree["children"]:
            is_list = self.check_if_list(prev_element, child)

            if not is_list:
                regex += self.create_regex(child)
            else:
                regex = self.mark_list_in_regex(regex, child["tag"])

            prev_element = child

        if generalized_tree["has_closing_tag"]:
            regex += "</" + generalized_tree["tag"] + ">"

        if is_optional:
            regex += ")?"

        return regex
