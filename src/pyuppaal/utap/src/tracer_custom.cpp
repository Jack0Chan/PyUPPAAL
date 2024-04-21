// -*- mode: C++; c-file-style: "stroustrup"; c-basic-offset: 4; indent-tabs-mode: nil; -*-

/* tracer - Utility for printing UPPAAL XTR trace files.
   Copyright (C) 2006 Uppsala University and Aalborg University.
   Copyright (C) 2017 Aalborg University.

   This library is free software; you can redistribute it and/or
   modify it under the terms of the GNU Lesser General Public License
   as published by the Free Software Foundation; either version 2.1 of
   the License, or (at your option) any later version.

   This library is distributed in the hope that it will be useful, but
   WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
   Lesser General Public License for more details.

   You should have received a copy of the GNU Lesser General Public
   License along with this library; if not, write to the Free Software
   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
   USA
*/

#include <fstream>
#include <iostream>
#include <sstream>
#include <limits>
#include <map>
#include <stdexcept>
#include <string>
#include <vector>

#include <cstdlib>
#include <cstring>
#include <cassert>
#include "cmdline.h"

/* This utility takes an UPPAAL model in the UPPAAL intermediate
 * format and a UPPAAL XTR trace file and prints trace to stdout in a
 * human readable format.
 *
 * The utility basically contains two parsers: One for the
 * intermediate format and one for the XTR format. You may want to use
 * them a starting point for writing analysis tools.
 *
 * Notice that the intermediate format uses a global numbering of
 * clocks, variables, locations, etc. This is in contrast to the XTR
 * format, which makes a clear distinction between e.g. clocks and
 * variables and uses process local number of locations and
 * edges. Care must be taken to convert between these two numbering
 * schemes.
 */

using std::ostream;
using std::istream;
using std::ifstream;
using std::ofstream;
using std::cout;
using std::cerr;
using std::endl;
using std::string;
using std::vector;
using std::map;


/* Representation of a memory cell.
 */
struct cell_t
{
    enum type_t : int { CONST, CLOCK, VAR, META, SYS_META, COST, LOCATION, FIXED };
    enum flags_t : int { NONE, COMMITTED, URGENT };
    /** The type of the cell. */
    type_t type;

    /** Name of cell. Not all types have names. */
    string name;

    union
    {
        int value;
        struct
        {
            int nr;
        } clock;
        struct
        {
            int min;
            int max;
            int init;
            int nr;
        } var;
        struct
        {
            int min;
            int max;
            int init;
            int nr;
        } meta;
        struct
        {
            int min;
            int max;
        } sys_meta;
        struct
        {
            flags_t flags;
            int process;
            int invariant;
        } location;
        struct
        {
            int min;
            int max;
        } fixed;
    };
};

/* Representation of a process.
 */
struct process_t
{
    int initial;
    string name;
    vector<int> locations;
    vector<int> edges;
};

/* Representation of an edge.
 */
struct edge_t
{
    int process;
    int source;
    int target;
    int guard;
    int sync;
    int update;
};

/* The UPPAAL model in intermediate format.
 */
static vector<cell_t> layout;
static vector<int> instructions;
static vector<process_t> processes;
static vector<edge_t> edges;
static map<int, string> expressions;

/* For convenience we keep the size of the system here.
 */
static size_t processCount = 0;
static size_t variableCount = 0;
static size_t clockCount = 0;

/* These are mappings from variable and clock indicies to
 * the names of these variables and clocks.
 */
static vector<string> clocks;
static vector<string> variables;

/* Thrown by parser upon parse errors.
 */
class invalid_format : public std::runtime_error
{
public:
    explicit invalid_format(const string& arg) : runtime_error(arg) {}
};

/* Reads one line from file. Skips comments.
 */
bool read(istream& file, string& str)
{
    do
    {
        if (!getline(file, str))
        {
            return false;
        }
    } while (!str.empty() && str[0] == '#');
    return true;
}

bool is_blank(const std::string& text)
{
    for (auto& c : text)
        if (!std::isspace(c))
            return false;
    return true;
}

/* Reads one line and asserts that it contains a (terminating) dot
 */
istream& readdot(istream& is)
{
    string str;
    while (getline(is, str) && is_blank(str))
        ;

    if (str != ".")
    {
        cerr << "Expecting a line with '.' but got ";
        if (!is)
            cerr << " end of file" << endl;
        else
            cerr << "'" << str << "'" << endl;
        assert(false);
        cerr << "Hint1: this may because .if file does not match .xtr file" << endl;
        cerr << "Hint2: or because of file encoding CRLF on Linux. Use LF for .if and .xtr file" << endl; 
        exit(EXIT_FAILURE);
    }
    return is;
}

inline
istream& skipspaces(istream& is)
{
    while (is.peek() == ' ')
    {
        is.get();
    }
    return is;
}

/* Parser for intermediate format.
 */
void loadIF(istream& file)
{
    string str;
    string section;
    char name[32];
    int index;

    while (getline(file, section))
    {
        if (section == "layout")
        {
            cell_t cell;
            while (read(file, str) && !str.empty() && !isspace(str[0]))
            {
                char s[6];
                auto cstr = str.c_str();

                if (sscanf(cstr, "%d:clock:%d:%31s", &index,
                    &cell.clock.nr, name) == 3)
                {
                    cell.type = cell_t::CLOCK;
                    cell.name = name;
                    clocks.emplace_back(name);
                    clockCount++;
                }
                else if (sscanf(cstr, "%d:const:%d", &index,
                    &cell.value) == 2)
                {
                    cell.type = cell_t::CONST;
                }
                else if (sscanf(cstr, "%d:var:%d:%d:%d:%d:%31s", &index,
                    &cell.var.min, &cell.var.max, &cell.var.init,
                    &cell.var.nr, name) == 6)
                {
                    cell.type = cell_t::VAR;
                    cell.name = name;
                    variables.emplace_back(name);
                    variableCount++;
                }
                else if (sscanf(cstr, "%d:meta:%d:%d:%d:%d:%31s", &index,
                    &cell.meta.min, &cell.meta.max, &cell.meta.init,
                    &cell.meta.nr, name) == 6)
                {
                    cell.type = cell_t::META;
                    cell.name = name;
                    variables.emplace_back(name);
                    variableCount++;
                }
                else if (sscanf(cstr, "%d:sys_meta:%d:%d:%31s", &index,
                    &cell.sys_meta.min, &cell.sys_meta.max, name) == 4)
                {
                    cell.type = cell_t::SYS_META;
                    cell.name = name;
                }
                else if (sscanf(cstr, "%d:location::%31s", &index, name) == 2)
                {
                    cell.type = cell_t::LOCATION;
                    cell.location.flags = cell_t::NONE;
                    cell.name = name;
                }
                else if (sscanf(cstr, "%d:location:committed:%31s", &index, name) == 2)
                {
                    cell.type = cell_t::LOCATION;
                    cell.location.flags = cell_t::COMMITTED;
                    cell.name = name;
                }
                else if (sscanf(cstr, "%d:location:urgent:%31s", &index, name) == 2)
                {
                    cell.type = cell_t::LOCATION;
                    cell.location.flags = cell_t::URGENT;
                    cell.name = name;
                }
                else if (sscanf(cstr, "%d:static:%d:%d:%31s", &index,
                    &cell.fixed.min, &cell.fixed.max,
                    name) == 4)
                {
                    cell.type = cell_t::FIXED;
                    cell.name = name;
                }
                else if (sscanf(cstr, "%d:%5s", &index, s) == 2
                    && strcmp(s, "cost") == 0)
                {
                    cell.type = cell_t::COST;
                }
                else
                {
                    throw invalid_format(str);
                }

                layout.push_back(cell);
            }
#if defined(ENABLE_CORA) || defined(ENABLE_PRICED)
            cell.type = cell_t::VAR;
            cell.var.min = std::numeric_limits<int32_t>::min();
            cell.var.max = std::numeric_limits<int32_t>::max();
            cell.var.init = 0;

            cell.name = "infimum_cost";
            cell.var.nr = variableCount++;
            variables.push_back(cell.name);
            layout.push_back(cell);

            cell.name = "offset_cost";
            cell.var.nr = variableCount++;
            variables.push_back(cell.name);
            layout.push_back(cell);

            for (size_t i = 1; i < clocks.size(); ++i) {
                cell.name = "#rate[";
                cell.name.append(clocks[i]);
                cell.name.append("]");
                cell.var.nr = variableCount++;
                variables.push_back(cell.name);
                layout.push_back(cell);
            }
#endif
        }
        else if (section == "instructions")
        {
            while (read(file, str) && !str.empty() && (!isspace(str[0]) || str[0] == '\t'))
            {
                int address;
                int values[4];
                if (str[0] == '\t')
                {   // skip pretty-printed instruction text
                    continue;
                }
                int cnt = sscanf(str.c_str(), "%d:%d%d%d%d", &address,
                    &values[0], &values[1], &values[2], &values[3]);
                if (cnt < 2)
                {
                    throw invalid_format("In instruction section when loading .if file.");
                }

                for (int i = 0; i < cnt - 1; ++i)
                {
                    instructions.push_back(values[i]);
                }
            }
        }
        else if (section == "processes")
        {
            while (read(file, str) && !str.empty() && !isspace(str[0]))
            {
                process_t process;
                if (sscanf(str.c_str(), "%d:%d:%31s",
                    &index, &process.initial, name) != 3)
                {
                    throw invalid_format("In process section when loading .if file.");
                }
                process.name = name;
                processes.push_back(process);
                processCount++;
            }
        }
        else if (section == "locations")
        {
            while (read(file, str) && !str.empty() && !isspace(str[0]))
            {
                int index;
                int process;
                int invariant;

                if (sscanf(str.c_str(), "%d:%d:%d", &index, &process, &invariant) != 3)
                {
                    throw invalid_format("In location section when loading .if file.");
                }

                layout[index].location.process = process;
                layout[index].location.invariant = invariant;
                processes[process].locations.push_back(index);
            }
        }
        else if (section == "edges")
        {
            while (read(file, str) && !str.empty() && !isspace(str[0]))
            {
                edge_t edge;

                if (sscanf(str.c_str(), "%d:%d:%d:%d:%d:%d", &edge.process,
                    &edge.source, &edge.target,
                    &edge.guard, &edge.sync, &edge.update) != 6)
                {
                    throw invalid_format("In edge section when loading .if file.");
                }

                processes[edge.process].edges.push_back(edges.size());
                edges.push_back(edge);
            }
        }
        else if (section == "expressions")
        {
            while (read(file, str) && !str.empty() && !isspace(str[0]))
            {
                if (sscanf(str.c_str(), "%d", &index) != 1)
                {
                    throw invalid_format("In expression section when loading .if file.");
                }

                /* Find expression string (after the third colon). */
                auto* s = str.c_str();
                int cnt = 3;
                while (cnt && *s)
                {
                    cnt -= (*s == ':');
                    s++;
                }
                if (cnt)
                {
                    throw invalid_format("In expression section when loading .if file.");
                }

                /* Trim white space. */
                while (*s && isspace(*s))
                {
                    s++;
                }
                auto* t = s + strlen(s) - 1;
                while (t >= s && isspace(*t))
                {
                    t--;
                }

                expressions[index] = string(s, t + 1);
            }
        }
        else
        {
        cerr << "The section:" << section << " is unknown." << endl;
        cerr << "Hint: The encoding/eol/body of the file may be wrong. Use LF instead of CRLF. Especially for Windows User." << endl;
        throw invalid_format("ERROR: Unknown section when loading .if file.");
        }
    }
};

/* A bound for a clock constraint. A bound consists of a value and a
 * bit indicating whether the bound is strict or not.
 */
struct bound_t
{
    int value : 31; // The value of the bound
    bool strict : 1;  // True if the bound is strict
};

/* The bound (infinity, <).
 */
static bound_t infinity = { std::numeric_limits<int32_t>::max() >> 1, true };

/* The bound (0, <=).
 */
static bound_t zero = { 0, false };

/* A symbolic state. A symbolic state consists of a location vector, a
 * variable vector and a zone describing the possible values of the
 * clocks in a symbolic manner.
 */
class State
{
public:
    State();
    explicit State(istream& file);
    State(const State& s) = delete;
    State(State&& s) = delete;
    ~State();

    int& getLocation(int i) { return locations[i]; }
    int& getVariable(int i) { return integers[i]; }
    bound_t& getConstraint(int i, int j) { return dbm[i * clockCount + j]; }

    int getLocation(int i) const { return locations[i]; }
    int getVariable(int i) const { return integers[i]; }
    bound_t getConstraint(int i, int j) const { return dbm[i * clockCount + j]; }
private:
    vector<int> locations;
    vector<int> integers;
    bound_t* dbm;
    void allocate();
};

State::~State()
{
    delete[] dbm;
}

State::State()
{
    /* Allocate. */
    locations.resize(processCount);
    integers.resize(variableCount);
    dbm = new bound_t[clockCount * clockCount];

    /* Fill with default values. */
    std::fill(dbm, dbm + clockCount * clockCount, infinity);

    /* Set diagonal and lower bounds to zero. */
    for (size_t i = 0; i < clockCount; i++)
    {
        getConstraint(0, i) = zero;
        getConstraint(i, i) = zero;
    }
}



State::State(istream& file) : State()
{
    /* Read locations.  */
    if (locations.empty()) {
        cerr << "WARNGING: The size of location is 0, maybe the .if file encoded incorrectly." << endl;
    }
    for (auto& l : locations)
    {
        file >> l;
    }
    file >> readdot;

    /* Read DBM. */
    int i, j, bnd;
    while (file >> i >> j >> bnd)
    {
        file >> readdot;
        getConstraint(i, j).value = bnd >> 1;
        getConstraint(i, j).strict = bnd & 1;
    }
    file.clear();
    file >> readdot;

    /* Read integers. */
    for (auto& v : integers)
    {
        file >> v;
    }
    file >> readdot;
}

struct Edge
{
    int process;
    int edge;
    vector<int> select;
};

/* A transition consists of one or more edges. Edges are indexes from
 * 0 in the order they appear in the input file.
 */
struct Transition
{
    vector<Edge> edges;
    explicit Transition(istream& file);
};

Transition::Transition(istream& file)
{
    int process, edge, select;
    while (file >> process >> edge)
    {
        Edge e{ process, edge };
        file >> skipspaces;
        while (file.peek() != '\n' && file.peek() != ';')
        {
            if (file >> select)
            {
                e.select.push_back(select);
            }
            else
            {
                cerr << "Transition format error" << endl;
                exit(EXIT_FAILURE);
            }
            file >> skipspaces;
        }
        if (file.get() == '\n') // old format without ';'
        {   // old format indexes edges from 1, hence convert to 0-base
            e.edge--;
        }
        edges.push_back(e);
    }
    file.clear();
    file >> readdot;
}

/* Output operator for a symbolic state. Prints the location vector,
 * the variables and the zone of the symbolic state.
 */
ostream& operator << (ostream& o, const State& state)
{
    /* Print location vector. */
    for (size_t p = 0; p < processCount; p++)
    {
        int idx = processes[p].locations[state.getLocation(p)];
        cout << processes[p].name << '.' << layout[idx].name << " ";
    }

    /* Print variables. */
    for (size_t v = 0; v < variableCount; v++)
    {
        cout << variables[v] << "=" << state.getVariable(v) << ' ';
    }

    /* Print clocks. */
    for (size_t i = 0; i < clockCount; i++)
    {
        for (size_t j = 0; j < clockCount; j++)
        {
            if (i != j)
            {
                bound_t bnd = state.getConstraint(i, j);

                if (bnd.value != infinity.value)
                {
                    cout << clocks[i] << "-" << clocks[j]
                        << (bnd.strict ? "<" : "<=") << bnd.value << " ";
                }
            }
        }
    }

    return o;
}

/* Output operator for a transition. Prints all edges in the
 * transition including the source, destination, guard,
 * synchronisation and assignment.
 */
ostream& operator << (ostream& o, const Transition& t)
{
    for (auto& edge : t.edges)
    {
        int eid = processes[edge.process].edges[edge.edge];
        int src = edges[eid].source;
        int dst = edges[eid].target;
        int guard = edges[eid].guard;
        int sync = edges[eid].sync;
        int update = edges[eid].update;
        cout << processes[edge.process].name << '.' << layout[src].name
            << " -> "
            << processes[edge.process].name << '.' << layout[dst].name;
        if (!edge.select.empty()) {
            auto s = edge.select.begin(), se = edge.select.end();
            cout << " [" << *s;
            while (++s != se) cout << "," << *s;
            cout << "]";
        }
        cout << " {"
            << expressions[guard] << "; " << expressions[sync] << "; " << expressions[update]
            << ";} ";
    }

    return o;
}

// ???????????
void Stringsplit(const string& str, const string& splits, vector<string>& res)
{
    if (str == "")		return;
    //????????��???????????????????????
    string strs = str + splits;
    size_t pos = strs.find(splits);
    int step = splits.size();

    // ?????????????????????????????? npos
    while (pos != strs.npos)
    {
        string temp = strs.substr(0, pos);
        res.push_back(temp);
        //?????????????,????????????��??��??
        strs = strs.substr(pos + step, strs.size());
        pos = strs.find(splits);
    }
}

vector<string> get_variables(string process_name) {
    //TODO
    //????process_name ????aa.t?��?aa????????????t
    vector<string> ret_val;

    for (size_t i = 0; i < clockCount; i++)
    {
        vector<string> strList2;
        Stringsplit(clocks[i], ".", strList2);
        bool flag = false;
        for (size_t i = 0; i < strList2.size(); i++)
        {
            if (strList2[i] == process_name)
            {
                flag = true;
                continue;
            }
            if (flag)
            {
                ret_val.push_back(strList2[i]);
            }
        }
        //cout << clocks[i] << endl;//???????clocks i/j ??

    }

    return ret_val;
}

//????????��????????????????guard????guard?????constraint
string get_guard_constraint(Transition& next_transition) {

    //??????????????
    //??????????��????????guard?1???????��????
    //??????????guard?????????????guard?????constraint

    string ret_val = "";
    for (auto& edge : next_transition.edges)//?????????????????????????????????
    {
        int eid = processes[edge.process].edges[edge.edge];
        int guard_index = edges[eid].guard;
        expressions[guard_index];//?????????guard????????????1??????guard

        if (expressions[guard_index] == "1")
        {
            continue;//??????????????��???????????????????�ʦ�???
        }

        processes[edge.process].name;//??????????????template???
        vector<string> var_list = get_variables(processes[edge.process].name);//????????????????��
        //TODO??????????????????????????????????????????aa.t????????
        //??????????????????????

    }
    return "Not implemented Error";

}

/* Read and print a trace file.
 */
void loadTrace(istream& file)
{
    /* Read and print trace. */

    //???????????????state??????????state??trace
    //??????????trace?????state
    State* prev_state = new State(file);
    bool printed_first_state = false;

    //cout << "State: " << State(file) << endl;
    for (;;)
    {
        /* Skip white space. */
        file >> skipspaces;

        /* A dot terminates the trace. */
        if (file.peek() == '.')
        {
            file.get();
            break;
        }

        /* Read a state and a transition. */
        State* this_state = new State(file);
        Transition transition(file);

        
        string added_constraint = get_guard_constraint(transition);
        //TODO??????????constraint???????

        /* Print transition and state. */
        cout << "\nState: " << *prev_state << endl;
        cout << "\nTransition: " << transition << endl;
        delete prev_state;
        prev_state = this_state;
    }
    cout << "\nState: " << *prev_state << endl;
}


int main(int argc, char* argv[])
{
    cmdline::parser my_parser;
    // ??????????????????
    // ?????????????????
    // ??????????????????'\0'?????��??????
    // ??????????????????��????
    // ???????????bool????????????????????????????????false??
    // ????????????????????????????????????????false????????��??
    my_parser.add<string>("trace", 't', "xtr trace file", true);
    my_parser.add<string>("if", 'i', "input the if file", false, "");
    my_parser.add<string>("string_if", 's', "input .if in string form", false, "");
    my_parser.add<string>("output_file", 'o', "output as file", false, "");

    my_parser.parse_check(argc, argv);
    for (size_t i = 0; i < my_parser.rest().size(); i++)
        cout << "- " << my_parser.rest()[i] << endl;

    try
    {
        if (my_parser.get<string>("if") != "" && my_parser.get<string>("string_if") != "")
        {
            printf("Only filling in one of the -if or -string_if will be accepted\n");
            exit(1);
        }
        if (my_parser.get<string>("if") == "" && my_parser.get<string>("string_if") == "")
        {
            printf("You have to specify either -if or -string_if.\n");
            exit(1);
        }
        //if (argc < 3)
        //{
        //    printf("Syntax: %s <if> <trace> [outputfile]. <> is necessary, [] is optional \n", argv[0]);
        //    exit(1);
        //}
        if (my_parser.get<string>("output_file") != "")
        {
            freopen(my_parser.get<string>("output_file").c_str(), "w", stdout);
        }

        /* Load model in intermediate format.
         */

        if (my_parser.get<string>("string_if") != "")
        {
            std::istringstream obj(my_parser.get<string>("string_if"));
            loadIF(obj);
        }
        else
        {
            ifstream file(my_parser.get<string>("if"));
            if (!file)
            {
                perror(my_parser.get<string>("if").c_str());
                exit(EXIT_FAILURE);
            }
            loadIF(file);
            file.close();
        }

        /* Load trace.
         */
        ifstream file(my_parser.get<string>("trace"));
        if (!file)
        {
            perror(my_parser.get<string>("trace").c_str());
            exit(EXIT_FAILURE);
        }
        loadTrace(file);
        file.close();
    }
    catch (std::exception& e)
    {
        cerr << "Cought exception: " << e.what() << endl;
    }
}
