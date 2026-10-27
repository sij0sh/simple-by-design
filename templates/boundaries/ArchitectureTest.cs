// Copy into a test project that references NetArchTest.Rules and xUnit.
// Replace the assembly names and namespaces with the repository's own.

using System.Reflection;
using NetArchTest.Rules;
using Xunit;

namespace Architecture.Tests;

public sealed class ArchitectureTest
{
    private static readonly Assembly[] Modules =
    {
        Assembly.Load("Orders"),
        Assembly.Load("Billing"),
    };

    [Fact]
    public void Domain_does_not_depend_on_frameworks_or_adapters()
    {
        var result = Types.InAssemblies(Modules)
            .That().ResideInNamespaceMatching(@".*\.Domain$")
            .ShouldNot().HaveDependencyOnAny(
                "Microsoft.AspNetCore",
                "Microsoft.EntityFrameworkCore",
                "System.Net.Http")
            .GetResult();

        Assert.True(result.IsSuccessful);
    }

    [Fact]
    public void Shared_does_not_depend_on_capabilities()
    {
        var result = Types.InAssemblies(Modules)
            .That().ResideInNamespaceMatching(@".*\.Shared$")
            .ShouldNot().HaveDependencyOnAny(
                "Orders",
                "Billing")
            .GetResult();

        Assert.True(result.IsSuccessful);
    }
}
