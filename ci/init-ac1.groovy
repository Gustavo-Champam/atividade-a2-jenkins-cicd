import jenkins.model.Jenkins
import hudson.security.HudsonPrivateSecurityRealm
import hudson.security.FullControlOnceLoggedInAuthorizationStrategy
import org.jenkinsci.plugins.workflow.job.WorkflowJob
import org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition
import hudson.plugins.git.GitSCM
import hudson.plugins.git.UserRemoteConfig
import hudson.plugins.git.BranchSpec

def j=Jenkins.get()
def realm=new HudsonPrivateSecurityRealm(false)
realm.createAccount('gustavo-a2',System.getenv('JENKINS_PASSWORD'))
j.setSecurityRealm(realm)
def auth=new FullControlOnceLoggedInAuthorizationStrategy()
auth.setAllowAnonymousRead(false)
j.setAuthorizationStrategy(auth)
j.setNumExecutors(1)
def xml = new File(System.getenv('GITHUB_WORKSPACE')+'/ci/ac1-job.xml').text
j.createProjectFromXML('A2_P1_AC1_Equipe',new ByteArrayInputStream(xml.getBytes('UTF-8')))
j.save()
