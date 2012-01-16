INSTALLATION

1. Install Apache Thrift: http://thrift.apache.org/
2. Copy maven-thrift-plugin source: git clone https://github.com/dtrott/maven-thrift-plugin.git
   Compile and install plugin into local repository: mvn clean install
   or add the following to your settings.xml to download the plugin:
            <pluginRepositories>
                <pluginRepository>
                    <id>dtrott</id>
                    <url>http://maven.davidtrott.com/repository</url>
                </pluginRepository>
            </pluginRepositories>
3. Cross your fingers and execute "mvn clean install" in the "authservice" directory