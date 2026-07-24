using System.Reflection;
using System.Runtime.Loader;

if (args.Length < 2)
{
    Console.Error.WriteLine("Usage: mcx-settings <mcx-dir> inspect|set [name=value ...]");
    return 2;
}

var mcxDir = Path.GetFullPath(args[0]);
var command = args[1].ToLowerInvariant();
AssemblyLoadContext.Default.Resolving += (_, name) =>
{
    var candidate = Path.Combine(mcxDir, name.Name + ".dll");
    return File.Exists(candidate) ? AssemblyLoadContext.Default.LoadFromAssemblyPath(candidate) : null;
};

var assemblies = Directory.EnumerateFiles(mcxDir, "*.dll")
    .Select(path =>
    {
        try { return AssemblyLoadContext.Default.LoadFromAssemblyPath(path); }
        catch { return null; }
    })
    .Where(assembly => assembly is not null)
    .Cast<Assembly>()
    .ToList();

var settingsTypes = assemblies.SelectMany(assembly =>
{
    try { return assembly.GetTypes(); }
    catch (ReflectionTypeLoadException ex) { return ex.Types.Where(type => type is not null)!; }
})
.Where(type => type is not null && type.Name.Contains("Settings", StringComparison.OrdinalIgnoreCase))
.ToList();

if (command == "inspect")
{
    var configurationAssembly = Assembly.Load("System.Configuration.ConfigurationManager");
    var clientPaths = configurationAssembly.GetType("System.Configuration.ClientConfigPaths");
    if (clientPaths is not null)
    {
        foreach (var method in clientPaths.GetMethods(BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Static))
            Console.WriteLine($"CONFIGPATHS|{method}");
        var getPaths = clientPaths.GetMethod("GetPaths", BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Static);
        var resolved = getPaths?.Invoke(null, new object[] { Path.Combine(mcxDir, "ModelConverterX.exe"), true });
        if (resolved is not null)
        {
            foreach (var property in clientPaths.GetProperties(BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance))
            {
                if (property.Name.Contains("Config", StringComparison.OrdinalIgnoreCase))
                    Console.WriteLine($"CONFIGVALUE|{property.Name}|{property.GetValue(resolved)}");
            }
        }
    }
    foreach (var type in settingsTypes.OrderBy(type => type.FullName))
    {
        var properties = type.GetProperties(BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance | BindingFlags.Static)
            .Where(property => property.Name.Contains("BGLComp", StringComparison.OrdinalIgnoreCase)
                || property.Name.Contains("MakeMDL", StringComparison.OrdinalIgnoreCase)
                || property.Name.Contains("Permission", StringComparison.OrdinalIgnoreCase)
                || property.Name.Contains("Copyright", StringComparison.OrdinalIgnoreCase)
                || property.Name.Contains("Reminder", StringComparison.OrdinalIgnoreCase));
        foreach (var property in properties)
            Console.WriteLine($"{type.Assembly.GetName().Name}|{type.FullName}|{property.Name}|{property.PropertyType.FullName}|write={property.CanWrite}|static={property.GetMethod?.IsStatic}");
        foreach (var method in type.GetMethods(BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance | BindingFlags.Static)
                     .Where(method => method.Name.Contains("Save", StringComparison.OrdinalIgnoreCase)
                         || method.Name.Contains("Setting", StringComparison.OrdinalIgnoreCase)))
            Console.WriteLine($"METHOD|{type.FullName}|{method.Name}|static={method.IsStatic}");
    }
    return 0;
}

if (command != "set")
{
    Console.Error.WriteLine($"Unknown command: {command}");
    return 2;
}

var requested = args.Skip(2)
    .Select(value => value.Split('=', 2))
    .Where(parts => parts.Length == 2)
    .ToDictionary(parts => parts[0], parts => parts[1], StringComparer.OrdinalIgnoreCase);
var changed = 0;

foreach (var type in settingsTypes)
{
    var changedThisType = false;
    foreach (var property in type.GetProperties(BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Static))
    {
        if (!property.CanWrite || property.PropertyType != typeof(string)) continue;
        if (!requested.TryGetValue(property.Name, out var value)) continue;
        property.SetValue(null, value);
        Console.WriteLine($"SET {type.FullName}.{property.Name}={value}");
        changed++;
        changedThisType = true;
    }

    var save = type.GetMethod("Save", BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Static, Type.EmptyTypes);
    if (changedThisType && save is not null)
        save.Invoke(null, null);
}

if (changed == 0)
{
    Console.Error.WriteLine("No matching writable MCX settings were found.");
    return 1;
}

return 0;
