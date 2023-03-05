INSERT INTO contest_event (old_id, updated, created, updated_by_id, owner_id, name, date_of_event, date_resolution, contest_id, notes, venue_id, complete, no_contest, contest_type_id, original_owner)
  VALUES (
    {{ContestEvent.id}},
    CONVERT(datetime, '{{ContestEvent.last_modified|date:"Y-m-d H:i:s"}}', 20),
    CONVERT(datetime, '{{ContestEvent.created|date:"Y-m-d H:i:s"}}', 20),
    (SELECT id FROM site_user WHERE usercode='{{ContestEvent.owner.username}}'),
    (SELECT id FROM site_user WHERE usercode='{{ContestEvent.lastChangedBy.username}}'),
    '{{ContestEvent.name_migrate|safe}}',
    CONVERT(date, '{{ContestEvent.date_of_event.day}}-{{ContestEvent.date_of_event.month}}-{{ContestEvent.date_of_event.year}}', 105),
    '{{ContestEvent.date_resolution}}',
    (SELECT id FROM contest WHERE old_id={{ContestEvent.contest.id}}),
    '{{ContestEvent.notes_migrate|safe}}',
    {% if ContestEvent.venue_link %}(SELECT id FROM venue WHERE old_id={{ContestEvent.venue_link.id}}){% else %}null{% endif %},
    {% if ContestEvent.complete %}1{%else%}0{%endif%},
    {% if ContestEvent.no_contest %}1{%else%}0{%endif%},
{% if ContestEvent.contest_type_override_link %}
  (SELECT id FROM contest_type WHERE old_id = {{ContestEvent.contest_type_override_link.id}}),
{% else %}
  (SELECT id FROM contest_type WHERE old_id = {{ContestEvent.contest.contest_type_link.id}}),
{% endif %}
    '{{ContestEvent.original_owner.username}}'
  );

{% if ContestEvent.test_piece %}
INSERT INTO contest_event_test_piece (updated, created, updated_by_id, owner_id, contest_event_id, piece_id, and_or)
VALUES (
    CONVERT(datetime, '{{ContestEvent.last_modified|date:"Y-m-d H:i:s"}}', 20),
    CONVERT(datetime, '{{ContestEvent.created|date:"Y-m-d H:i:s"}}', 20),
    (SELECT id FROM site_user WHERE usercode='{{ContestEvent.owner.username}}'),
    (SELECT id FROM site_user WHERE usercode='{{ContestEvent.lastChangedBy.username}}'),
    (SELECT id FROM contest_event WHERE old_id = {{ContestEvent.id}}),
    {{ContestEvent.test_piece.id}},
    null
);
{%endif%}

{% for piece in ContestEvent.contesttestpiece_set.all %}
INSERT INTO contest_event_test_piece (updated, created, updated_by_id, owner_id, contest_event_id, piece_id, and_or)
VALUES (
    CONVERT(datetime, '{{ContestEvent.last_modified|date:"Y-m-d H:i:s"}}', 20),
    CONVERT(datetime, '{{ContestEvent.created|date:"Y-m-d H:i:s"}}', 20),
    (SELECT id FROM site_user WHERE usercode='{{ContestEvent.owner.username}}'),
    (SELECT id FROM site_user WHERE usercode='{{ContestEvent.lastChangedBy.username}}'),
    (SELECT id FROM contest_event WHERE old_id = {{ContestEvent.id}}),
    {{piece.test_piece.id}},
    {% if piece.and_or == 'and' %}
    'A'
    {% elif piece.and_or == 'or' %}
    'O'
    {% else %}
    null
    {% endif %}
);
{% endfor %}

{% for result in ContestEvent.contestresult_set.all %}
INSERT INTO contest_result (old_id, updated, created, updated_by_id, owner_id, contest_event_id, band_id, band_name, result_position_type, result_position, draw, draw_second, 
                            points_total, points_first, points_second, points_third, points_fourth, points_penalty, conductor_name, conductor_id, conductor_two_id, notes)
VALUES (
  {{result.id}},
  CONVERT(datetime, '{{result.last_modified|date:"Y-m-d H:i:s"}}', 20),
  CONVERT(datetime, '{{result.created|date:"Y-m-d H:i:s"}}', 20),
  (SELECT id FROM site_user WHERE usercode='{{result.owner.username}}'),
  (SELECT id FROM site_user WHERE usercode='{{result.lastChangedBy.username}}'),
  (SELECT id FROM contest_event WHERE old_id={{ContestEvent.id}}),
  (SELECT id FROM band WHERE old_id={{result.band.id}}),
  '{{result.band_name_export|safe}}',
{% if result.results_position_display == 'W' %}
  'W',
{% elif result.results_position_display == 'D' %}  
  'D',
{% elif result.results_position_display == '' %}
  'U',
{% else %}
  'R',
{% endif %}
{% if result.results_position_display == 'W' %}
  null,
{% elif result.results_position_display == 'D' %}  
  null,
{% elif result.results_position_display == '' %}
  null,
{% else %}
  {{result.results_position_display}},
{% endif %}
  {{result.draw}},
{% if result.draw_second_part %}
  {{result.draw_second_part}},
{% else %}
  null,
{% endif %}
  '{{result.points}}',
  '{{result.points_first_part}}',
  '{{result.points_second_part}}',
  '{{result.points_third_part}}',
  '{{result.points_fourth_part}}',
  '{{result.penalty_points}}',
  '{{result.conductor_name}}',
  (SELECT id FROM person WHERE old_id={{result.person_conducting.id}}),
  {% if result.second_person_conducting %}
  (SELECT id FROM person WHERE old_id={{result.second_person_conducting.id}}),
  {% else %}
  null,
  {% endif %}
  '{{result.notes_migrate|safe}}'
);

{% if result.test_piece %}
INSERT INTO contest_result_test_piece (updated, created, updated_by_id, owner_id, contest_result_id, piece_id, ordering, suffix)
VALUES (
  CONVERT(datetime, '{{result.last_modified|date:"Y-m-d H:i:s"}}', 20),
  CONVERT(datetime, '{{result.created|date:"Y-m-d H:i:s"}}', 20),
  (SELECT id FROM site_user WHERE usercode='{{result.owner.username}}'),
  (SELECT id FROM site_user WHERE usercode='{{result.lastChangedBy.username}}'),
  (SELECT id FROM contest_result WHERE old_id = {{result.id}}),
  (SELECT id FROM piece WHERE old_id = {{result.test_piece.id}}),
  0,
  null
);
{% endif %}

{% for extra_piece in result.resultpieceperformance_set.all %}
INSERT INTO contest_result_test_piece (updated, created, updated_by_id, owner_id, contest_result_id, piece_id, ordering, suffix)
VALUES (
  CONVERT(datetime, '{{result.last_modified|date:"Y-m-d H:i:s"}}', 20),
  CONVERT(datetime, '{{result.created|date:"Y-m-d H:i:s"}}', 20),
  (SELECT id FROM site_user WHERE usercode='{{result.owner.username}}'),
  (SELECT id FROM site_user WHERE usercode='{{result.lastChangedBy.username}}'),
  (SELECT id FROM contest_result WHERE old_id = {{result.id}}),
  (SELECT id FROM piece WHERE old_id = {{extra_piece.piece.id}}),
  {{extra_piece.ordering}},
  '{{extra_piece.suffix}}'
);
{% endfor %}

{% endfor %}