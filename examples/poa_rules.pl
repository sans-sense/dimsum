component(bar).
component(content_view).
component(control).
component(status_bar).
component(tab_bar).
component(icon_grid).

component(network_activity_indicator).
component(page_control).
component(battery_indicator).
component(signal_indicator).
component(icon_content_view).


screen(home).
screen(app).

isOfType(Screen, home) :-
    hasComponent(Screen, status_bar),
    hasComponent(Screen, page_control),
    hasComponent(Screen, icon_grid),
    hasComponent(Screen, tab_bar).


isOfType(Screen, launch_start) :-
    isOfType(Screen, home),
    hasNoDistortedIcon(Screen),
    isOfType(immediatePrevious, home),
    hasFadedIcon(Screen).

isOfType(Screen, transitory) :-
    not(hasComponent(Screen, status_bar)).

isOfType(Screen, transitory) :-
    hasOverlaps(immediatePrevious).

isOfType(Screen, transitory) :-
    not(hasComponent(Screen, qwerty_kb)),
    not(hasComponent(Screen, tab_bar)).

isOfType(Screen, network_active) :-
    hasComponent(Screen, network_activity_indicator).

isOfType(Screen, scrolling_active) :-
    hasOverlaps(immediatePrevious),
    isOverlap(topways).

isOfType(Screen, launch_lf_transitory) :-
    isScaled(immediatePrevious).

isOfType(Screen, app_kill) :-
    isOfType(Screen, transitory),
    hasText(Screen, recents).

isOfType(Screen, app_kill) :-
    isOfType(Screen, transitory),
    isOfType(immediatePrevious, app_kill).


%% define hasFadedIcon, hasNoDistortedIcon
%% status_bar should have a time component
