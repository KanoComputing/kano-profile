

from kano_profile.badges import calculate_badges


def filter_item_info():
    '''This is a dictionary of the names and the corresponding
    bg colour, badge description etc.
    '''
    badge_dictionary = calculate_badges()['badges']
    badge_list = []

    for category, cat_dict in badge_dictionary.iteritems():
        for filename, item_dict in cat_dict.iteritems():
            if 'order' not in item_dict:
                item_dict['order'] = 0
            item_dict['category'] = category
            item_dict['name'] = filename

            badge_list.append(item_dict)

    badge_list = sorted(badge_list, key=lambda k: k['order'], reverse=False)

    return badge_list


def create_item_page_list():
    '''Split the badges into pages
    so we can show the correct number.
    '''
    badge_list = filter_item_info()

    max_row = 2
    max_column = 3
    number_on_a_page = max_row * max_column

    number_of_badges = 0
    row = 0
    column = 0
    page = 0

    page_list = []
    page_list.append([])

    for badge_info in badge_list:

        badge_info["row"] = row
        badge_info['column'] = column
        badge_info['page'] = page

        page_list[page].append(badge_info)

        column += 1
        number_of_badges += 1

        if number_of_badges == number_on_a_page:
            page += 1
            row = 0
            column = 0
            number_of_badges = 0
            page_list.append([])

        if column == max_column:
            column = 0
            row += 1

    return (badge_list, page_list)
