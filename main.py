from dataclasses import dataclass
from bakery import assert_equal
from drafter import *


@dataclass
class Project:
    """Store the information for one civil engineering project."""
    name: str
    project_type: str
    location: str
    budget: float
    materials: list["Material"]
    completed: bool


@dataclass
class State:
    """Store information that is shared between website routes."""
    username: str
    projects: list[Project]
    current_project: str
    total_budget: float
    page: str
    message: str


@dataclass
class Material:
    """Store one material and its estimated cost."""
    name: str
    quantity: float
    unit: str
    price_per_unit: float


def concrete_volume(length: float, width: float,
                    thickness: float) -> float:
    """Calculate the volume of a concrete slab in cubic feet."""
    return length * width * thickness


def cubic_yards(cubic_feet: float) -> float:
    """Convert cubic feet to cubic yards."""
    return cubic_feet / 27


def material_cost(quantity: float, price_per_unit: float) -> float:
    """Calculate the cost of one material."""
    return quantity * price_per_unit


def total_material_cost(materials: list[Material]) -> float:
    """Calculate the combined cost of all project materials."""
    total = 0.0
    for material in materials:
        total = total + material_cost(
            material.quantity, material.price_per_unit
        )
    return total


def update_total_budget(projects: list[Project]) -> float:
    """Add the budgets for all projects in the project list."""
    total = 0.0
    for project in projects:
        total = total + project.budget
    return total


def find_project(projects: list[Project],
                 project_name: str) -> Project:
    """Find a project by name, or return an empty project if not found."""
    for project in projects:
        if project.name == project_name:
            return project
    return Project("", "", "", 0.0, [], False)


# Tests for the helper functions.
assert_equal(concrete_volume(20, 15, 0.5), 150)
assert_equal(cubic_yards(27), 1)
assert_equal(material_cost(5.5, 120), 660)
assert_equal(total_material_cost([
    Material("Concrete", 10, "cubic yards", 150),
    Material("Rebar", 20, "pieces", 8)
]), 1660)
assert_equal(update_total_budget([
    Project("Road", "Road", "Newark", 1000.0, [], False),
    Project("Bridge", "Bridge", "Newark", 2500.0, [], True)
]), 3500.0)
assert_equal(find_project([
    Project("Road", "Road", "Newark", 1000.0, [], False)
], "Road").budget, 1000.0)


@route
def index(state: State) -> Page:
    """Show the homepage and project dashboard."""
    state.page = "Dashboard"
    return Page(state, [
        Header("Civil Engineering Project Hub"),
        Text("Plan and organize small construction and infrastructure projects."),

        Header("Welcome"),
        Text("Enter your name to personalize the dashboard:"),
        TextBox("username", state.username),
        Button("Save Name", "save_username"),
        Text(state.message),

        Header("Project Overview"),
        Text("Welcome, " + state.username + "!"),
        Text("Number of projects: " + str(len(state.projects))),
        Text("Combined project budget: $" +
             str(round(state.total_budget, 2))),

        Header("What would you like to do?"),
        Text("Choose one of the buttons below to open a tool or page."),
        Button("Create a New Project", "create_project"),
        Button("View All Projects", "projects"),
        Button("Calculate Materials", "calculate_materials"),
        Button("Concrete Volume Calculator", "material_calculator"),
        Button("Material Cost Estimator", "cost_estimator"),
        Button("Civil Engineering Resources", "resources")
    ])


@route
def save_username(state: State, username: str) -> Page:
    """Save the username entered on the dashboard."""
    if username.strip() == "":
        state.message = "Please enter a name."
    else:
        state.username = username
        state.message = "Name saved."
    return index(state)


@route
def create_project(state: State) -> Page:
    """Show the form used to create a project."""
    state.page = "Create Project"
    return Page(state, [
        Header("Create a Project"),
        Text("Fill in the project details below."),
        Text("Project name:"),
        TextBox("name"),
        Text("Project type:"),
        SelectBox("project_type", [
            "Road", "Bridge", "Foundation", "Drainage", "Other"
        ]),
        Text("Project location:"),
        TextBox("location"),
        Text("Estimated project budget in dollars:"),
        TextBox("budget", "0", "number"),
        Button("Create Project", "add_project"),
        Text(state.message),
        Button("Back to Dashboard", "index")
    ])


@route
def add_project(state: State, name: str, project_type: str,
                location: str, budget: float) -> Page:
    """Validate project information and create a new project."""
    if name.strip() == "":
        state.message = "Project name cannot be empty."
        return create_project(state)

    if location.strip() == "":
        state.message = "Please enter a project location."
        return create_project(state)

    if budget < 0:
        state.message = "The budget cannot be negative."
        return create_project(state)

    new_project = Project(name, project_type, location, budget, [], False)
    state.projects.append(new_project)
    state.total_budget = update_total_budget(state.projects)
    state.current_project = name
    state.message = "Project created. You can add materials on the Calculate Materials page."
    return project_details(state, name)


@route
def calculate_materials(state: State) -> Page:
    """Show the separate page for choosing materials for a project."""
    state.page = "Calculate Materials"

    if len(state.projects) == 0:
        return Page(state, [
            Header("Calculate Materials"),
            Text("Create a project before adding materials."),
            Button("Create a Project", "create_project"),
            Button("Dashboard", "index")
        ])

    project_names = []
    for project in state.projects:
        project_names.append(project.name)

    return Page(state, [
        Header("Calculate Materials"),
        Text("Choose the project you want to add materials to."),
        Text("Project:"),
        SelectBox("project_name", project_names),
        Text("Check each material you need and enter its quantity."),
        Header("Available Materials and Estimated Prices"),
        Text("Concrete - $150 per cubic yard"),
        CheckBox("concrete"),
        Text("Concrete quantity (cubic yards):"),
        TextBox("concrete_quantity", "1", "number"),
        Text("Rebar - $8 per piece"),
        CheckBox("rebar"),
        Text("Rebar quantity (pieces):"),
        TextBox("rebar_quantity", "1", "number"),
        Text("Asphalt - $110 per ton"),
        CheckBox("asphalt"),
        Text("Asphalt quantity (tons):"),
        TextBox("asphalt_quantity", "1", "number"),
        Text("Gravel - $35 per ton"),
        CheckBox("gravel"),
        Text("Gravel quantity (tons):"),
        TextBox("gravel_quantity", "1", "number"),
        Text("Steel Beams - $500 per beam"),
        CheckBox("steel_beams"),
        Text("Steel beam quantity:"),
        TextBox("steel_quantity", "1", "number"),
        Text("Lumber - $12 per board"),
        CheckBox("lumber"),
        Text("Lumber quantity (boards):"),
        TextBox("lumber_quantity", "1", "number"),
        Text("PVC Pipe - $4 per foot"),
        CheckBox("pvc_pipe"),
        Text("PVC pipe quantity (feet):"),
        TextBox("pipe_quantity", "1", "number"),
        Text("Sand - $30 per ton"),
        CheckBox("sand"),
        Text("Sand quantity (tons):"),
        TextBox("sand_quantity", "1", "number"),
        Button("Save Selected Materials", "save_materials"),
        Text(state.message),
        Button("View All Projects", "projects"),
        Button("Dashboard", "index")
    ])


@route
def save_materials(state: State, project_name: str,
                  concrete: bool, concrete_quantity: float,
                  rebar: bool, rebar_quantity: float,
                  asphalt: bool, asphalt_quantity: float,
                  gravel: bool, gravel_quantity: float,
                  steel_beams: bool, steel_quantity: float,
                  lumber: bool, lumber_quantity: float,
                  pvc_pipe: bool, pipe_quantity: float,
                  sand: bool, sand_quantity: float) -> Page:
    """Save checked materials and their quantities to the project."""
    project = find_project(state.projects, project_name)
    if project.name == "":
        state.message = "That project could not be found."
        return projects(state)

    selections = [
        (concrete, "Concrete", concrete_quantity, "cubic yards", 150),
        (rebar, "Rebar", rebar_quantity, "pieces", 8),
        (asphalt, "Asphalt", asphalt_quantity, "tons", 110),
        (gravel, "Gravel", gravel_quantity, "tons", 35),
        (steel_beams, "Steel Beams", steel_quantity, "beams", 500),
        (lumber, "Lumber", lumber_quantity, "boards", 12),
        (pvc_pipe, "PVC Pipe", pipe_quantity, "feet", 4),
        (sand, "Sand", sand_quantity, "tons", 30)
    ]

    selected_materials = []
    for selected, material_name, quantity, unit, price in selections:
        if selected:
            if quantity <= 0:
                state.message = "Enter a quantity greater than zero for each selected material."
                return calculate_materials(state)
            selected_materials.append(Material(
                material_name, quantity, unit, price
            ))

    if len(selected_materials) == 0:
        state.message = "Please select at least one material."
        return calculate_materials(state)

    project.materials = selected_materials
    state.message = "Materials saved successfully."
    return project_details(state, project_name)


@route
def projects(state: State) -> Page:
    """Display all saved projects."""
    state.page = "All Projects"

    contents = [
        Header("All Projects"),
        Text("Select a project to see its materials and budget estimate."),
        Header("Saved Project List")
    ]

    if len(state.projects) == 0:
        contents.append(Text("No projects have been added yet."))
    else:
        for project in state.projects:
            if project.completed:
                status = "Completed"
            else:
                status = "In Progress"

            contents.append(Header(project.name))
            contents.append(Text("Type: " + project.project_type))
            contents.append(Text("Location: " + project.location))
            contents.append(Text(
                "Budget: $" + str(round(project.budget, 2))
            ))
            contents.append(Text(
                "Material estimate: $" +
                str(round(total_material_cost(project.materials), 2))
            ))
            contents.append(Text("Status: " + status))
            contents.append(Button(
                "View Project: " + project.name,
                "project_details",
                arguments={"project_name": project.name}
            ))

    contents.append(Button("Calculate Materials", "calculate_materials"))
    contents.append(Button("Create Another Project", "create_project"))
    contents.append(Button("Back to Dashboard", "index"))
    return Page(state, contents)


@route
def project_details(state: State, project_name: str) -> Page:
    """Show project materials, costs, and budget comparison."""
    state.page = "Project Details"
    project = find_project(state.projects, project_name)

    if project.name == "":
        state.message = "That project could not be found."
        return projects(state)

    state.current_project = project.name
    material_total = total_material_cost(project.materials)

    contents = [
        Header("Project Details"),
        Header(project.name),
        Text("Type: " + project.project_type),
        Text("Location: " + project.location),
        Text("Project budget: $" + str(round(project.budget, 2))),
        Header("Materials Needed and Estimated Costs")
    ]

    if len(project.materials) == 0:
        contents.append(Text(
            "No materials have been entered for this project yet."
        ))
    else:
        for material in project.materials:
            item_total = material_cost(
                material.quantity, material.price_per_unit
            )
            contents.append(Header(material.name))
            contents.append(Text(
                "Quantity: " + str(material.quantity) + " " + material.unit
            ))
            contents.append(Text(
                "Price per unit: $" +
                str(round(material.price_per_unit, 2))
            ))
            contents.append(Text(
                "Material total: $" + str(round(item_total, 2))
            ))

    contents.append(Header("Budget Summary"))
    contents.append(Text(
        "Total estimated material cost: $" +
        str(round(material_total, 2))
    ))

    if len(project.materials) == 0:
        contents.append(Text(
            "Enter materials to see whether the project is within budget."
        ))
    elif material_total <= project.budget:
        remaining = project.budget - material_total
        contents.append(Text("Budget status: WITHIN BUDGET"))
        contents.append(Text(
            "Remaining budget: $" + str(round(remaining, 2))
        ))
    else:
        over_budget = material_total - project.budget
        contents.append(Text("Budget status: OVER BUDGET"))
        contents.append(Text(
            "Amount over budget: $" + str(round(over_budget, 2))
        ))

    if project.completed:
        contents.append(Text("Project status: Completed"))
    else:
        contents.append(Text("Project status: In Progress"))
        contents.append(Button(
            "Mark Project Complete",
            "complete_project",
            arguments={"project_name": project.name}
        ))

    contents.append(Text(state.message))
    contents.append(Button("Calculate / Edit Materials", "calculate_materials"))
    contents.append(Button("All Projects", "projects"))
    contents.append(Button("Create Another Project", "create_project"))
    contents.append(Button("Dashboard", "index"))
    return Page(state, contents)


@route
def material_calculator(state: State) -> Page:
    """Show the concrete slab volume calculator."""
    state.page = "Material Calculator"
    return Page(state, [
        Header("Concrete Material Calculator"),
        Text("Estimate the concrete needed for a rectangular slab."),

        Header("Enter Dimensions"),
        Text("Enter all dimensions in feet."),
        Text("Length:"),
        TextBox("length", 20, "number"),
        Text("Width:"),
        TextBox("width", 15, "number"),
        Text("Thickness:"),
        TextBox("thickness", 0.5, "number"),

        Button("Calculate Concrete", "calculate_concrete"),
        Text(state.message),
        Text("Formula: length x width x thickness."),
        Button("Dashboard", "index"),
        Button("All Projects", "projects")
    ])


@route
def calculate_concrete(state: State, length: float,
                       width: float, thickness: float) -> Page:
    """Calculate concrete volume in cubic feet and cubic yards."""
    if length <= 0 or width <= 0 or thickness <= 0:
        state.message = "All dimensions must be greater than zero."
        return material_calculator(state)

    volume = concrete_volume(length, width, thickness)
    yards = cubic_yards(volume)
    state.message = (
        "Concrete needed: " + str(round(volume, 2)) +
        " cubic feet, or " + str(round(yards, 2)) +
        " cubic yards. This is a basic estimate."
    )
    return material_calculator(state)


@route
def cost_estimator(state: State) -> Page:
    """Show the general material cost estimator."""
    state.page = "Cost Estimator"
    return Page(state, [
        Header("Material Cost Estimator"),
        Text("Estimate the cost of any material, not just concrete."),
        Header("Cost Information"),
        Text("Enter the material quantity and price per unit."),
        Text("Quantity:"),
        TextBox("quantity", 5, "number"),
        Text("Price per unit in dollars:"),
        TextBox("price_per_unit", 100, "number"),
        Button("Estimate Cost", "calculate_cost"),
        Text(state.message),
        Button("Dashboard", "index"),
        Button("All Projects", "projects")
    ])


@route
def calculate_cost(state: State, quantity: float,
                   price_per_unit: float) -> Page:
    """Calculate the estimated cost of a material."""
    if quantity < 0 or price_per_unit < 0:
        state.message = "Quantity and price cannot be negative."
    else:
        estimate = material_cost(quantity, price_per_unit)
        state.message = (
            "Estimated material cost: $" + str(round(estimate, 2))
        )
    return cost_estimator(state)


@route
def resources(state: State) -> Page:
    """Show introductory information about civil engineering topics."""
    state.page = "Engineering Resources"
    return Page(state, [
        Header("Civil Engineering Resources"),
        Text("Explore short introductions to common civil engineering areas."),

        Header("Roads"),
        Text("Road projects involve pavement layers, grading, drainage, "
             "traffic needs, and material selection."),

        Header("Bridges"),
        Text("Bridge projects require engineers to consider loads, spans, "
             "structural members, foundations, and safety."),

        Header("Foundations"),
        Text("Foundations transfer building loads into the ground. Soil "
             "conditions and structural loads affect foundation design."),

        Header("Stormwater and Drainage"),
        Text("Drainage systems move runoff away from roads and buildings. "
             "Engineers consider rainfall, runoff, slopes, and pipe capacity."),

        Text("These descriptions are introductory and are not engineering "
             "design guidance."),
        Button("Dashboard", "index"),
        Button("All Projects", "projects")
    ])


@route
def complete_project(state: State, project_name: str) -> Page:
    """Mark the selected project as completed."""
    found = False

    for project in state.projects:
        if project.name == project_name:
            project.completed = True
            found = True

    if found:
        state.message = project_name + " has been marked complete."
    else:
        state.message = "Project not found."

    state.total_budget = update_total_budget(state.projects)
    return project_details(state, project_name)


hide_debug_information()
set_website_title("Civil Engineering Project Hub")

set_site_information(
    author="Treyvon Shaffer",
    description="A tool for organizing basic construction projects and estimates.",
    sources="Drafter documentation and CISC108 class materials.",
    planning=["Copy-of-CSI-Final-Project-1_Design.docx"],
    links=[]
)

start_server(State("", [], "", 0.0, "Dashboard", ""))
