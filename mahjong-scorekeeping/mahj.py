import flet as ft

def main(page: ft.Page):
    page.title = "Mahjong Scorekeeping"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO
    page.window.height = 800
    page.window.width = 650

    # --- STATE VARIABLES ---
    player_scores = {}
    current_round = 1

    level_checkboxes = {}
    level_name_inputs = {}
    level_score_inputs = {}
    level_double_displays = {}
    round_history_data = []
    # level_rows = {}

    levels = [3, 4, 5, 6, 7, 8, 9, 10, 13]

    # --- SCREEN 1: SETUP CONTROLS ---
    txt_p1 = ft.TextField(label="Player 1", width=85, value="P1")
    txt_p2 = ft.TextField(label="Player 2", width=85, value="P2")
    txt_p3 = ft.TextField(label="Player 3", width=85, value="P3")
    txt_p4 = ft.TextField(label="Player 4", width=85, value="P4")

    lbl_setup_error = ft.Text(value="", color=ft.Colors.RED_ACCENT, visible=False)

    def update_all_calculated_fields():
        try:
            current_value = int(level_score_inputs[1].value)
            for i in range(2, 10):
                level_score_inputs[i].value = str(int(level_score_inputs[i-1].value) * 2)
        except ValueError:
            pass

        for i in range(1, 10):
            try:
                level_double_displays[i].value = str(int(level_score_inputs[i].value) * 2)
            except ValueError:
                level_double_displays[i].value = ""
        page.update()

    def toggle_level_active(e):
        for i, chk in level_checkboxes.items():
            if chk == e.control:
                level_name_inputs[i].disabled = not chk.value
                level_score_inputs[i].disabled = not chk.value
                level_double_displays[i].disabled = not chk.value
                # level_rows[i].update()
                break
        page.update()

    level_rows_list = []
    for i, fann in enumerate(levels, start=1):
        # chk_box = ft.Checkbox(value=True, on_change=toggle_level_active)
        chk_box = ft.Checkbox(value=True, width=40)
        name_field = ft.TextField(value=f"{fann} 番", width=90, dense=True)
        score_field = ft.TextField(
            value="4" if i == 1 else "",
            keyboard_type=ft.KeyboardType.NUMBER,
            width=90,
            dense=True,
            on_change=update_all_calculated_fields if i == 1 else None,
            read_only = i > 1,
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST if i > 1 else None,
            color=ft.Colors.OUTLINE if i > 1 else None
        )

        double_field = ft.TextField(
            value="", width=90, dense=True, read_only=True,
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST, color=ft.Colors.OUTLINE
        )

        level_checkboxes[i] = chk_box
        level_name_inputs[i] = name_field
        level_score_inputs[i] = score_field
        level_double_displays[i] = double_field

        row_instance = ft.Row([
            chk_box, name_field, ft.Text(":"), score_field, double_field
        ], alignment=ft.MainAxisAlignment.CENTER)

        # level_rows[i] = row_instance
        level_rows_list.append(row_instance)

    update_all_calculated_fields()

    # --- SCREEN 2: SCOREBOARD CONTROLS ---
    lbl_round = ft.Text(value="Round 1", size=24, weight=ft.FontWeight.BOLD)
    scoreboard_container = ft.Column(spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    drp_winner = ft.Dropdown(label="贏家", width=100)
    drp_level_achieved = ft.Dropdown(label="番數", width=110)
    drp_winning_method = ft.Dropdown(label="自摸/出銃", width=140)
    lbl_game_error = ft.Text(value="", color=ft.Colors.RED_ACCENT, weight=ft.FontWeight.BOLD)

    history_list_view = ft.ListView(spacing=5, padding=10, height=140, auto_scroll=True)

    def update_payment_options(e):
        winner = drp_winner.value
        if not winner:
            return

        options = [ft.dropdown.Option(key="self", text="自摸")]
        for player in player_scores.keys():
            options.append(ft.dropdown.Option(key=player, text=f"{player} 出銃"))

        drp_winning_method.options = options
        drp_winning_method.value = "self"
        page.update()

    drp_winner.on_change = update_payment_options

    # --- APP LOGIC FUNCTIONS ---

    def start_game(e):
        nonlocal player_scores, current_round, round_history_data

        if not (txt_p1.value and txt_p2.value and txt_p3.value and txt_p4.value):
            lbl_setup_error.value = "Please fill in all player names!"
            lbl_setup_error.visible=True
            page.update()
            return

        has_at_least_one_level = False
        try:
            for i in range(1, 10):
                if level_checkboxes[i].value:
                    has_at_least_one_level = True
                    if not level_name_inputs[i].value.strip():
                        lbl_setup_error.value = f"Please enter a name for Row {i}!"
                        lbl_setup_error.visible = True
                        page.update()
                        return
                    int(level_score_inputs[i].value)
        except ValueError:
            lbl_setup_error.value = "Active score fields must contain valid numbers!"
            lbl_setup_error.visible = True
            page.update()
            return

        if not has_at_least_one_level:
            lbl_setup_error.value = "You must select at least one level to play!"
            lbl_setup_error.visible = True
            page.update()
            return

        player_scores = {
            txt_p1.value.strip(): 0,
            txt_p2.value.strip(): 0,
            txt_p3.value.strip(): 0,
            txt_p4.value.strip(): 0
        }

        current_round = 1
        round_history_data.clear()
        history_list_view.controls.clear()
        lbl_round.value = "Round 0"

        page.controls.clear()

        player_names_list = list(player_scores.keys())
        drp_winner.options = [ft.dropdown.Option(name) for name in player_names_list]
        drp_winner.value = player_names_list[0]

        method_options = [ft.dropdown.Option(key="self", text="Self 自摸")]
        for name in player_names_list:
            method_options.append(ft.dropdown.Option(key=name, text=f"{name} 出銃"))

        drp_winning_method.options = method_options
        drp_winning_method.value = "self"

        dropdown_options = []
        first_valid_key = None
        for i in range(1, 10):
            if level_checkboxes[i].value:
                dropdown_options.append(ft.dropdown.Option(key=str(i), text=level_name_inputs[i].value))
                if first_valid_key is None:
                    first_valid_key = str(i)

        drp_level_achieved.options = dropdown_options
        drp_level_achieved.value = first_valid_key

        update_payment_options(None)
        update_score_display()

        page.add(
            ft.Row([ft.Button("← Back to Setup and RESET ALL", on_click=show_setup_screen,
                              bgcolor=ft.Colors.RED, color=ft.Colors.WHITE)
                              # bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST, color=ft.Colors.ON_SURFACE)
                    ], alignment = ft.MainAxisAlignment.CENTER),
            ft.Card(content=ft.Container(content=ft.Column([
                lbl_round, scoreboard_container,
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER), padding=20)),
            ft.Divider(),
            ft.Text("Log Round Result", size=18, weight=ft.FontWeight.BOLD),
            ft.Row([drp_winner, drp_level_achieved, drp_winning_method], alignment=ft.MainAxisAlignment.CENTER),
            lbl_game_error,
            ft.Row([
                ft.Button("Submit", on_click=submit_round, bgcolor=ft.Colors.BLUE, color=ft.Colors.WHITE),
                ft.Button("Undo Last", on_click=undo_round, bgcolor=ft.Colors.ORANGE, color=ft.Colors.WHITE),
                # ft.Button("Reset", on_click=reset_game, bgcolor=ft.Colors.RED, color=ft.Colors.WHITE),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
            ft.Divider(),
            ft.Text("Game History Log", size=16, weight=ft.FontWeight.W_500),
            ft.Container(
                content=history_list_view,
                border=ft.BorderSide(1, ft.Colors.OUTLINE_VARIANT),
                border_radius=5,
                bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
                width=550,
                height=160
            ),
            ft.Text("© 2026 Mahjong Scorekeeper v1.0. All rights reserved.", size=12, color=ft.Colors.OUTLINE)
        )
        page.update()

    def update_score_display():
        scoreboard_container.controls.clear()
        for player, score in player_scores.items():
            scoreboard_container.controls.append(ft.Row([
                ft.Text(f"{player}:", size=18, weight=ft.FontWeight.W_500),
                ft.Text(f"{score} pts", size=18, color=ft.Colors.GREEN if score >= 0 else ft.Colors.RED)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, width=250))

    def submit_round(e):
        nonlocal current_round
        lbl_game_error.value = ""

        winner = drp_winner.value
        method = drp_winning_method.value
        chosen_index = int(drp_level_achieved.value)
        level_name = level_name_inputs[chosen_index].value

        if winner == method:
            lbl_game_error.value = f"Error: {winner} cannot pay themselves! Select another option."
            page.update()
            return

        base_points = int(level_score_inputs[chosen_index].value)
        double_points = int(level_double_displays[chosen_index].value)

        score_changes = {player: 0 for player in player_scores.keys()}
        history_text = ""

        if method == "self":
            for player in player_scores.keys():
                if player == winner:
                    score_changes[winner] = base_points * 3
                else:
                    score_changes[player] = -base_points
            history_text = f"Round {current_round}: {winner} won | 自摸 {level_name}. Everyone paid {base_points} pts."
        else:
            target_loser = method
            score_changes[winner] = double_points
            score_changes[target_loser] = -double_points
            history_text = f"Round {current_round}: {winner} won | {target_loser} 出銃 {level_name}. {target_loser} paid {double_points} pts."

        for player, change in score_changes.items():
            player_scores[player] += change

        round_history_data.append(score_changes)

        history_list_view.controls.append(
            ft.Text(history_text, size=13, color=ft.Colors.ON_SURFACE_VARIANT)
        )

        lbl_round.value = f"Round {current_round}"
        current_round += 1
        update_score_display()
        page.update()

    def undo_round(e):
        nonlocal current_round
        lbl_game_error.value = ""

        if not round_history_data:
            lbl_game_error.value = "No rounds have been played yet!"
            page.update()
            return

        last_round_changes = round_history_data.pop()

        for player, change in last_round_changes.items():
            player_scores[player] -= change

        if history_list_view.controls:
            history_list_view.controls.pop()

        current_round -= 1
        lbl_round.value = f"Round {current_round}"
        update_score_display()
        page.update()

    def reset_game(e):
        nonlocal current_round
        lbl_game_error.value = ""

        for player in player_scores.keys():
            player_scores[player] = 0

        current_round = 1
        lbl_round.value = "Round 1"
        round_history_data.clear()
        history_list_view.controls.clear()

        update_score_display()
        page.update()

    # --- INITIAL SETUP SCREEN LAYOUT ---
    def show_setup_screen(e=None):
        page.controls.clear()
        lbl_setup_error.visible = False  # Reset error text visibility on return
        page.add(
            ft.Text("Score Setup", size=22, weight=ft.FontWeight.BOLD),
            ft.Row([txt_p1, txt_p2, txt_p3, txt_p4], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
            ft.Divider(),
            ft.Row([
                ft.Text("", width=40),
                ft.Text("\u00A0\u00A0\u00A0\u00A0Config", width=90, size=14, weight=ft.FontWeight.BOLD),
                ft.Text(":"),
                ft.Text("\u00A0\u00A0\u00A0自摸每人", width=90, size=14, weight=ft.FontWeight.BOLD),
                ft.Text("\u00A0\u00A0\u00A0全銃", width=90, size=14, weight=ft.FontWeight.BOLD),
            ], alignment=ft.MainAxisAlignment.CENTER),
            ft.Column(level_rows_list, spacing=5, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            ft.Text("Only uncheck top/bottom boxes.", color=ft.Colors.OUTLINE, width=330),
            lbl_setup_error,
            ft.Button("Start Scorekeeping", on_click=start_game, bgcolor=ft.Colors.GREEN, color=ft.Colors.WHITE),
            ft.Text(""),
            ft.Text("© 2026 Mahjong Scorekeeper v1.0. All rights reserved.", size=12, color=ft.Colors.OUTLINE)
        )
        page.update()

    # Call the setup screen initially to display it when the app starts
    show_setup_screen()

ft.run(main)
