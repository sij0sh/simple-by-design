package architecture;

import static com.tngtech.archunit.lang.syntax.ArchRuleDefinition.noClasses;
import static com.tngtech.archunit.library.dependencies.SlicesRuleDefinition.slices;

import com.tngtech.archunit.junit.AnalyzeClasses;
import com.tngtech.archunit.junit.ArchTest;
import com.tngtech.archunit.lang.ArchRule;

// Replace com.example and the module names with your base package and
// capabilities. Allow public api packages when a contract exists.
@AnalyzeClasses(packages = "com.example")
public class ArchitectureTest {

    @ArchTest
    static final ArchRule noModuleCycles =
        slices().matching("com.example.modules.(*)..")
            .should().beFreeOfCycles();

    @ArchTest
    static final ArchRule ordersDoNotUseBillingInternals =
        noClasses().that().resideInAPackage("..modules.orders..")
            .should().dependOnClassesThat()
            .resideInAnyPackage(
                "..modules.billing.domain..",
                "..modules.billing.persistence..");

    @ArchTest
    static final ArchRule billingDoesNotUseOrdersInternals =
        noClasses().that().resideInAPackage("..modules.billing..")
            .should().dependOnClassesThat()
            .resideInAnyPackage(
                "..modules.orders.domain..",
                "..modules.orders.persistence..");

    @ArchTest
    static final ArchRule sharedIsInfrastructure =
        noClasses().that().resideInAPackage("..shared..")
            .should().dependOnClassesThat().resideInAPackage("..modules..");
}
