import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
  AppLayout,
  ContentLayout,
  Header,
  SpaceBetween,
  Button,
  Cards,
  Box,
  ProgressBar,
  Badge,
  ColumnLayout,
  Container,
  SideNavigation,
  HelpPanel,
  Link,
  TopNavigation,
  ExpandableSection,
  Select,
  Textarea,
  Alert,
  Modal
} from '@cloudscape-design/components';

interface EvalResult {
  status: string;
  conversation: Array<{
    role: string;
    content: string;
    turn_number: number;
    timestamp: number;
  }>;
  modeling_session: string;
  data_model: string;
  session_evaluation?: {
    scores: {
      access_pattern_analysis: number;
      methodology_adherence: number;
      process_documentation: number;
      requirements_engineering: number;
      technical_reasoning: number;
    };
    overall_score: number;
    quality_level: string;
    justifications?: {
      overall: string;
      methodology: string;
      requirements: string;
      technical_depth: string;
    };
  };
  model_evaluation?: {
    scores: {
      completeness: number;
      technical_accuracy: number;
      access_pattern_coverage: number;
      scalability_considerations: number;
      cost_optimization: number;
    };
    overall_score: number;
    quality_level: string;
    justifications?: {
      overall: string;
      completeness: string;
      technical: string;
    };
  };
  quality_assessment: {
    session_quality_level: string;
    model_quality_level: string;
  };
  performance_metadata: {
    conversation_duration: number;
    session_evaluation_duration: number;
    model_evaluation_duration: number;
    total_duration: number;
  };
  timestamp: string;
}

interface Scenario {
  name: string;
  description: string;
  complexity: string;
  performance_and_scale: {
    user_base: string;
    transaction_volume: string;
    data_growth: string;
    read_write_ratio: string;
    performance_requirements: string[];
    scalability_needs: string;
    regional_requirements: string;
  };
  application_details: {
    type: string;
    domain: string;
    primary_function: string;
    business_model: string;
  };
  entities_and_relationships: {
    entities: Record<string, string>;
    relationships: string[];
  };
  access_patterns: {
    read_patterns: string[];
    write_patterns: string[];
  };
  expected_elements: string[];
  key_concepts_should_include: string[];
}

interface HistoryEntry {
  id: number;
  timestamp: string;
  scenario_name: string;
  result: EvalResult;
}

const App: React.FC = () => {
  const [isRunning, setIsRunning] = useState(false);
  const [results, setResults] = useState<EvalResult[]>([]);
  const [activeHref, setActiveHref] = useState('/dashboard');
  const [progress, setProgress] = useState(0);
  const [selectedScenario, setSelectedScenario] = useState({ label: 'Simple E-commerce Schema', value: 'Simple E-commerce Schema' });
  const [promptContent, setPromptContent] = useState('');
  const [promptLoading, setPromptLoading] = useState(false);
  const [promptSaving, setPromptSaving] = useState(false);
  const [promptAlert, setPromptAlert] = useState<{ type: 'success' | 'error', message: string } | null>(null);
  const [isPreviewMode, setIsPreviewMode] = useState(false);
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [modalVisible, setModalVisible] = useState(false);
  const [modalContent, setModalContent] = useState('');
  const [modalTitle, setModalTitle] = useState('');

  useEffect(() => {
    loadScenarios();
  }, []);

  useEffect(() => {
    if (activeHref === '/prompt-editor' && !promptContent) {
      loadPrompt();
    }
    if (activeHref === '/history') {
      loadHistory();
    }
  }, [activeHref]);

  const runEvaluation = async () => {
    setIsRunning(true);
    setProgress(0);
    
    // Simulate progress over 150 seconds (2.5 minutes)
    const progressInterval = setInterval(() => {
      setProgress(prev => {
        const increment = Math.random() * 3 + 1; // 1-4% increments
        const newProgress = Math.min(prev + increment, 95); // Cap at 95% until completion
        return newProgress;
      });
    }, 4000); // Update every 2 seconds
    
    try {
      const response = await fetch('http://localhost:5000/api/run-evaluation', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          scenario: selectedScenario.value
        })
      });
      
      clearInterval(progressInterval);
      setProgress(100);
      
      if (response.ok) {
        const result = await response.json();
        setResults(prev => [result, ...prev]);
      } else {
        const error = await response.json();
        console.error('Evaluation failed:', error);
        alert(`Evaluation failed: ${error.error}`);
      }
    } catch (error) {
      clearInterval(progressInterval);
      console.error('Error running evaluation:', error);
      alert('Failed to connect to evaluation service. Make sure the API server is running.');
    }
    setIsRunning(false);
    setProgress(0);
  };

  const getScoreColor = (score: number) => {
    if (score >= 8.5) return 'green';
    if (score >= 7.0) return 'blue';
    return 'red';
  };

  const formatDuration = (seconds: number) => {
    return `${Math.round(seconds)}s`;
  };

  const renderEvaluationResult = (result: EvalResult, index: number) => (
    <SpaceBetween key={index} direction="vertical" size="m">
      {/* Summary Card */}
      <Container
        header={
          <Header variant="h2">
            Evaluation Summary
            <Badge color={result.status === 'success' ? 'green' : 'red'}>
              {result.status}
            </Badge>
          </Header>
        }
      >
        <ColumnLayout columns={4} variant="text-grid">
          <div>
            <Box variant="awsui-key-label">Model Quality</Box>
            <Badge color={getScoreColor(result.model_evaluation?.overall_score || 0)}>
              {result.quality_assessment?.model_quality_level || 'unknown'}
            </Badge>
          </div>
          <div>
            <Box variant="awsui-key-label">Session Quality</Box>
            <Badge color={getScoreColor(result.session_evaluation?.overall_score || 0)}>
              {result.quality_assessment?.session_quality_level || 'unknown'}
            </Badge>
          </div>
          <div>
            <Box variant="awsui-key-label">Total Duration</Box>
            <Box>{formatDuration(result.performance_metadata.total_duration)}</Box>
          </div>
          <div>
            <Box variant="awsui-key-label">Conversation Turns</Box>
            <Box>{result.conversation.length}</Box>
          </div>
        </ColumnLayout>
      </Container>

      {/* Model Evaluation Card */}
      {result.model_evaluation && (
        <Container
          header={
            <Header 
              variant="h3"
              actions={
                <Button onClick={() => openModal('Data Model', result.data_model)}>
                  View Data Model
                </Button>
              }
            >
              Model Evaluation
              <Badge color={getScoreColor(result.model_evaluation.overall_score)}>
                {result.model_evaluation.overall_score}/10
              </Badge>
            </Header>
          }
        >
          <SpaceBetween direction="vertical" size="m">
            <ColumnLayout columns={3} variant="text-grid">
              <div>
                <Box variant="awsui-key-label">Completeness</Box>
                <Badge color={getScoreColor(result.model_evaluation.scores.completeness)}>
                  {result.model_evaluation.scores.completeness}/10
                </Badge>
              </div>
              <div>
                <Box variant="awsui-key-label">Technical Accuracy</Box>
                <Badge color={getScoreColor(result.model_evaluation.scores.technical_accuracy)}>
                  {result.model_evaluation.scores.technical_accuracy}/10
                </Badge>
              </div>
              <div>
                <Box variant="awsui-key-label">Access Patterns</Box>
                <Badge color={getScoreColor(result.model_evaluation.scores.access_pattern_coverage)}>
                  {result.model_evaluation.scores.access_pattern_coverage}/10
                </Badge>
              </div>
              <div>
                <Box variant="awsui-key-label">Scalability</Box>
                <Badge color={getScoreColor(result.model_evaluation.scores.scalability_considerations)}>
                  {result.model_evaluation.scores.scalability_considerations}/10
                </Badge>
              </div>
              <div>
                <Box variant="awsui-key-label">Cost Optimization</Box>
                <Badge color={getScoreColor(result.model_evaluation.scores.cost_optimization)}>
                  {result.model_evaluation.scores.cost_optimization}/10
                </Badge>
              </div>
            </ColumnLayout>
            
            {result.model_evaluation.justifications && (
              <ExpandableSection headerText="Detailed Justifications">
                <SpaceBetween direction="vertical" size="s">
                  <div>
                    <Box variant="h4">Overall Assessment</Box>
                    <Box>{result.model_evaluation.justifications.overall}</Box>
                  </div>
                  <div>
                    <Box variant="h4">Completeness</Box>
                    <Box>{result.model_evaluation.justifications.completeness}</Box>
                  </div>
                  <div>
                    <Box variant="h4">Technical Accuracy</Box>
                    <Box>{result.model_evaluation.justifications.technical}</Box>
                  </div>
                </SpaceBetween>
              </ExpandableSection>
            )}
          </SpaceBetween>
        </Container>
      )}

      {/* Session Evaluation Card */}
      {result.session_evaluation && (
        <Container
          header={
            <Header 
              variant="h3"
              actions={
                <Button onClick={() => openModal('Modeling Session', result.modeling_session)}>
                  View Session
                </Button>
              }
            >
              Session Evaluation
              <Badge color={getScoreColor(result.session_evaluation.overall_score)}>
                {result.session_evaluation.overall_score}/10
              </Badge>
            </Header>
          }
        >
          <SpaceBetween direction="vertical" size="m">
            <ColumnLayout columns={3} variant="text-grid">
              <div>
                <Box variant="awsui-key-label">Access Pattern Analysis</Box>
                <Badge color={getScoreColor(result.session_evaluation.scores.access_pattern_analysis)}>
                  {result.session_evaluation.scores.access_pattern_analysis}/10
                </Badge>
              </div>
              <div>
                <Box variant="awsui-key-label">Methodology Adherence</Box>
                <Badge color={getScoreColor(result.session_evaluation.scores.methodology_adherence)}>
                  {result.session_evaluation.scores.methodology_adherence}/10
                </Badge>
              </div>
              <div>
                <Box variant="awsui-key-label">Process Documentation</Box>
                <Badge color={getScoreColor(result.session_evaluation.scores.process_documentation)}>
                  {result.session_evaluation.scores.process_documentation}/10
                </Badge>
              </div>
              <div>
                <Box variant="awsui-key-label">Requirements Engineering</Box>
                <Badge color={getScoreColor(result.session_evaluation.scores.requirements_engineering)}>
                  {result.session_evaluation.scores.requirements_engineering}/10
                </Badge>
              </div>
              <div>
                <Box variant="awsui-key-label">Technical Reasoning</Box>
                <Badge color={getScoreColor(result.session_evaluation.scores.technical_reasoning)}>
                  {result.session_evaluation.scores.technical_reasoning}/10
                </Badge>
              </div>
            </ColumnLayout>
            
            {result.session_evaluation.justifications && (
              <ExpandableSection headerText="Detailed Justifications">
                <SpaceBetween direction="vertical" size="s">
                  <div>
                    <Box variant="h4">Overall Assessment</Box>
                    <Box>{result.session_evaluation.justifications.overall}</Box>
                  </div>
                  <div>
                    <Box variant="h4">Methodology</Box>
                    <Box>{result.session_evaluation.justifications.methodology}</Box>
                  </div>
                  <div>
                    <Box variant="h4">Requirements</Box>
                    <Box>{result.session_evaluation.justifications.requirements}</Box>
                  </div>
                  <div>
                    <Box variant="h4">Technical Depth</Box>
                    <Box>{result.session_evaluation.justifications.technical_depth}</Box>
                  </div>
                </SpaceBetween>
              </ExpandableSection>
            )}
          </SpaceBetween>
        </Container>
      )}
    </SpaceBetween>
  );

  const loadPrompt = async () => {
    setPromptLoading(true);
    try {
      const response = await fetch('http://localhost:5000/api/prompt');
      if (response.ok) {
        const data = await response.json();
        setPromptContent(data.content);
      } else {
        const error = await response.json();
        setPromptAlert({ type: 'error', message: `Failed to load prompt: ${error.error}` });
      }
    } catch (error) {
      setPromptAlert({ type: 'error', message: 'Failed to connect to API server' });
    }
    setPromptLoading(false);
  };

  const savePrompt = async () => {
    setPromptSaving(true);
    try {
      const response = await fetch('http://localhost:5000/api/prompt', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: promptContent })
      });
      
      if (response.ok) {
        setPromptAlert({ type: 'success', message: 'Prompt saved successfully' });
      } else {
        const error = await response.json();
        setPromptAlert({ type: 'error', message: `Failed to save prompt: ${error.error}` });
      }
    } catch (error) {
      setPromptAlert({ type: 'error', message: 'Failed to connect to API server' });
    }
    setPromptSaving(false);
  };

  const loadHistory = async () => {
    setHistoryLoading(true);
    try {
      const response = await fetch('http://localhost:5000/api/history');
      if (response.ok) {
        const data = await response.json();
        setHistory(data);
      } else {
        console.error('Failed to load history');
      }
    } catch (error) {
      console.error('Failed to connect to API server');
    }
    setHistoryLoading(false);
  };

  const loadScenarios = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/scenarios');
      if (response.ok) {
        const data = await response.json();
        setScenarios(data);
      } else {
        console.error('Failed to load scenarios');
      }
    } catch (error) {
      console.error('Failed to connect to API server');
    }
  };

  const openModal = (title: string, content: string) => {
    setModalTitle(title);
    setModalContent(content);
    setModalVisible(true);
  };

  const renderContent = () => {
    if (activeHref === '/history') {
      return (
        <ContentLayout
          header={
            <Header 
              variant="h1"
              actions={
                <Button onClick={loadHistory} loading={historyLoading}>
                  Refresh
                </Button>
              }
            >
              Evaluation History
            </Header>
          }
        >
          {history.length === 0 ? (
            <Box textAlign="center" color="inherit">
              <b>No evaluation history</b>
              <Box variant="p" color="inherit">
                Run some evaluations to see history here.
              </Box>
            </Box>
          ) : (
            <SpaceBetween direction="vertical" size="l">
              {history.map((entry) => (
                <Container
                  key={entry.id}
                  header={
                    <Header variant="h2">
                      <SpaceBetween direction="horizontal" size="s">
                        <Box>Evaluation Summary</Box>
                        <Badge color={entry.result.status === 'success' ? 'green' : 'red'}>
                          {entry.result.status}
                        </Badge>
                        <Box variant="small">{new Date(entry.timestamp).toLocaleString()}</Box>
                      </SpaceBetween>
                    </Header>
                  }
                >
                  <SpaceBetween direction="vertical" size="m">
                    <ColumnLayout columns={4} variant="text-grid">
                      <div>
                        <Box variant="awsui-key-label">Model Quality</Box>
                        <Badge color={getScoreColor(entry.result.model_evaluation?.overall_score || 0)}>
                          {entry.result.quality_assessment?.model_quality_level || 'unknown'}
                        </Badge>
                      </div>
                      <div>
                        <Box variant="awsui-key-label">Session Quality</Box>
                        <Badge color={getScoreColor(entry.result.session_evaluation?.overall_score || 0)}>
                          {entry.result.quality_assessment?.session_quality_level || 'unknown'}
                        </Badge>
                      </div>
                      <div>
                        <Box variant="awsui-key-label">Total Duration</Box>
                        <Box>{formatDuration(entry.result.performance_metadata.total_duration)}</Box>
                      </div>
                      <div>
                        <Box variant="awsui-key-label">Conversation Turns</Box>
                        <Box>{entry.result.conversation.length}</Box>
                      </div>
                    </ColumnLayout>
                    
                    <ExpandableSection headerText={`${entry.scenario_name} - Detailed Results`}>
                      <SpaceBetween direction="vertical" size="m">
                        {entry.result.model_evaluation && (
                          <Container
                            header={
                              <Header 
                                variant="h3"
                                actions={
                                  <Button onClick={() => openModal('Data Model', entry.result.data_model)}>
                                    View Data Model
                                  </Button>
                                }
                              >
                                Model Evaluation
                                <Badge color={getScoreColor(entry.result.model_evaluation.overall_score)}>
                                  {entry.result.model_evaluation.overall_score}/10
                                </Badge>
                              </Header>
                            }
                          >
                            <SpaceBetween direction="vertical" size="m">
                              <ColumnLayout columns={3} variant="text-grid">
                                <div>
                                  <Box variant="awsui-key-label">Completeness</Box>
                                  <Badge color={getScoreColor(entry.result.model_evaluation.scores.completeness)}>
                                    {entry.result.model_evaluation.scores.completeness}/10
                                  </Badge>
                                </div>
                                <div>
                                  <Box variant="awsui-key-label">Technical Accuracy</Box>
                                  <Badge color={getScoreColor(entry.result.model_evaluation.scores.technical_accuracy)}>
                                    {entry.result.model_evaluation.scores.technical_accuracy}/10
                                  </Badge>
                                </div>
                                <div>
                                  <Box variant="awsui-key-label">Access Patterns</Box>
                                  <Badge color={getScoreColor(entry.result.model_evaluation.scores.access_pattern_coverage)}>
                                    {entry.result.model_evaluation.scores.access_pattern_coverage}/10
                                  </Badge>
                                </div>
                                <div>
                                  <Box variant="awsui-key-label">Scalability</Box>
                                  <Badge color={getScoreColor(entry.result.model_evaluation.scores.scalability_considerations)}>
                                    {entry.result.model_evaluation.scores.scalability_considerations}/10
                                  </Badge>
                                </div>
                                <div>
                                  <Box variant="awsui-key-label">Cost Optimization</Box>
                                  <Badge color={getScoreColor(entry.result.model_evaluation.scores.cost_optimization)}>
                                    {entry.result.model_evaluation.scores.cost_optimization}/10
                                  </Badge>
                                </div>
                              </ColumnLayout>
                              
                              {entry.result.model_evaluation.justifications && (
                                <ExpandableSection headerText="Detailed Justifications">
                                  <SpaceBetween direction="vertical" size="s">
                                    <div>
                                      <Box variant="h4">Overall Assessment</Box>
                                      <Box>{entry.result.model_evaluation.justifications.overall}</Box>
                                    </div>
                                    <div>
                                      <Box variant="h4">Completeness</Box>
                                      <Box>{entry.result.model_evaluation.justifications.completeness}</Box>
                                    </div>
                                    <div>
                                      <Box variant="h4">Technical Accuracy</Box>
                                      <Box>{entry.result.model_evaluation.justifications.technical}</Box>
                                    </div>
                                  </SpaceBetween>
                                </ExpandableSection>
                              )}
                            </SpaceBetween>
                          </Container>
                        )}

                        {entry.result.session_evaluation && (
                          <Container
                            header={
                              <Header 
                                variant="h3"
                                actions={
                                  <Button onClick={() => openModal('Modeling Session', entry.result.modeling_session)}>
                                    View Session
                                  </Button>
                                }
                              >
                                Session Evaluation
                                <Badge color={getScoreColor(entry.result.session_evaluation.overall_score)}>
                                  {entry.result.session_evaluation.overall_score}/10
                                </Badge>
                              </Header>
                            }
                          >
                            <SpaceBetween direction="vertical" size="m">
                              <ColumnLayout columns={3} variant="text-grid">
                                <div>
                                  <Box variant="awsui-key-label">Access Pattern Analysis</Box>
                                  <Badge color={getScoreColor(entry.result.session_evaluation.scores.access_pattern_analysis)}>
                                    {entry.result.session_evaluation.scores.access_pattern_analysis}/10
                                  </Badge>
                                </div>
                                <div>
                                  <Box variant="awsui-key-label">Methodology Adherence</Box>
                                  <Badge color={getScoreColor(entry.result.session_evaluation.scores.methodology_adherence)}>
                                    {entry.result.session_evaluation.scores.methodology_adherence}/10
                                  </Badge>
                                </div>
                                <div>
                                  <Box variant="awsui-key-label">Process Documentation</Box>
                                  <Badge color={getScoreColor(entry.result.session_evaluation.scores.process_documentation)}>
                                    {entry.result.session_evaluation.scores.process_documentation}/10
                                  </Badge>
                                </div>
                                <div>
                                  <Box variant="awsui-key-label">Requirements Engineering</Box>
                                  <Badge color={getScoreColor(entry.result.session_evaluation.scores.requirements_engineering)}>
                                    {entry.result.session_evaluation.scores.requirements_engineering}/10
                                  </Badge>
                                </div>
                                <div>
                                  <Box variant="awsui-key-label">Technical Reasoning</Box>
                                  <Badge color={getScoreColor(entry.result.session_evaluation.scores.technical_reasoning)}>
                                    {entry.result.session_evaluation.scores.technical_reasoning}/10
                                  </Badge>
                                </div>
                              </ColumnLayout>
                              
                              {entry.result.session_evaluation.justifications && (
                                <ExpandableSection headerText="Detailed Justifications">
                                  <SpaceBetween direction="vertical" size="s">
                                    <div>
                                      <Box variant="h4">Overall Assessment</Box>
                                      <Box>{entry.result.session_evaluation.justifications.overall}</Box>
                                    </div>
                                    <div>
                                      <Box variant="h4">Methodology</Box>
                                      <Box>{entry.result.session_evaluation.justifications.methodology}</Box>
                                    </div>
                                    <div>
                                      <Box variant="h4">Requirements</Box>
                                      <Box>{entry.result.session_evaluation.justifications.requirements}</Box>
                                    </div>
                                    <div>
                                      <Box variant="h4">Technical Depth</Box>
                                      <Box>{entry.result.session_evaluation.justifications.technical_depth}</Box>
                                    </div>
                                  </SpaceBetween>
                                </ExpandableSection>
                              )}
                            </SpaceBetween>
                          </Container>
                        )}
                      </SpaceBetween>
                    </ExpandableSection>
                  </SpaceBetween>
                </Container>
              ))}
            </SpaceBetween>
          )}
        </ContentLayout>
      );
    }

    if (activeHref === '/prompt-editor') {
      return (
        <ContentLayout
          header={
            <Header 
              variant="h1"
              actions={
                <SpaceBetween direction="horizontal" size="s">
                  <Button 
                    onClick={() => setIsPreviewMode(!isPreviewMode)}
                    iconName={isPreviewMode ? "edit" : "external"}
                  >
                    {isPreviewMode ? "Edit" : "Preview"}
                  </Button>
                  <Button onClick={loadPrompt} loading={promptLoading}>
                    Reload
                  </Button>
                  <Button variant="primary" onClick={savePrompt} loading={promptSaving}>
                    Save Prompt
                  </Button>
                </SpaceBetween>
              }
            >
              Prompt Editor
            </Header>
          }
        >
          <SpaceBetween direction="vertical" size="m">
            {promptAlert && (
              <Alert
                type={promptAlert.type}
                dismissible
                onDismiss={() => setPromptAlert(null)}
              >
                {promptAlert.message}
              </Alert>
            )}
            
            <Container>
              {isPreviewMode ? (
                <div style={{ height: 'calc(100vh - 200px)', overflow: 'auto', padding: '16px' }}>
                  <ReactMarkdown 
                    remarkPlugins={[remarkGfm]}
                    components={{
                      table: ({children}) => <table style={{borderCollapse: 'collapse', width: '100%', margin: '16px 0'}}>{children}</table>,
                      th: ({children}) => <th style={{border: '1px solid #ddd', padding: '8px', backgroundColor: '#f5f5f5', fontWeight: 'bold'}}>{children}</th>,
                      td: ({children}) => <td style={{border: '1px solid #ddd', padding: '8px'}}>{children}</td>, 
                      pre: ({children}) => <pre style={{backgroundColor: '#f6f8fa', padding: '16px'}}>{children}</pre>,
                    }}
                  >
                    {promptContent}
                  </ReactMarkdown>
                </div>
              ) : (
                <Textarea
                  value={promptContent}
                  onChange={({ detail }) => setPromptContent(detail.value)}
                  placeholder="Loading prompt..."
                  disabled={promptLoading}
                  rows={Math.floor((window.innerHeight - 200) / 20)}
                />
              )}
            </Container>
          </SpaceBetween>
        </ContentLayout>
      );
    }

    if (activeHref === '/scenarios') {
      return (
        <ContentLayout
          header={<Header variant="h1">Evaluation Scenarios</Header>}
        >
          <Cards
            ariaLabels={{
              itemSelectionLabel: (e, t) => `select ${t.name}`,
              selectionGroupLabel: "Available scenarios"
            }}
            cardDefinition={{
              header: item => (
                <SpaceBetween direction="horizontal" size="xs">
                  <Box variant="h3">{item.name}</Box>
                  <Badge color={item.complexity === 'advanced' ? 'red' : 'blue'}>
                    {item.complexity}
                  </Badge>
                </SpaceBetween>
              ),
              sections: [
                {
                  id: "description",
                  content: item => <Box>{item.description}</Box>
                },
                {
                  id: "details",
                  content: item => (
                    <SpaceBetween direction="vertical" size="m">
                      <ColumnLayout columns={2} variant="text-grid">
                        <div>
                          <Box variant="awsui-key-label">User Base</Box>
                          <Box>{item.performance_and_scale.user_base}</Box>
                        </div>
                        <div>
                          <Box variant="awsui-key-label">Transaction Volume</Box>
                          <Box>{item.performance_and_scale.transaction_volume}</Box>
                        </div>
                      </ColumnLayout>
                      
                      <ExpandableSection headerText="Application Details">
                        <ColumnLayout columns={2} variant="text-grid">
                          <div>
                            <Box variant="awsui-key-label">Type</Box>
                            <Box>{item.application_details.type}</Box>
                          </div>
                          <div>
                            <Box variant="awsui-key-label">Domain</Box>
                            <Box>{item.application_details.domain}</Box>
                          </div>
                          <div>
                            <Box variant="awsui-key-label">Primary Function</Box>
                            <Box>{item.application_details.primary_function}</Box>
                          </div>
                          <div>
                            <Box variant="awsui-key-label">Business Model</Box>
                            <Box>{item.application_details.business_model}</Box>
                          </div>
                        </ColumnLayout>
                      </ExpandableSection>

                      <ExpandableSection headerText="Entities & Relationships">
                        <SpaceBetween direction="vertical" size="s">
                          <div>
                            <Box variant="h4">Entities</Box>
                            {Object.entries(item.entities_and_relationships.entities).map(([key, value]: [string, string]) => (
                              <div key={key}>
                                <Box variant="awsui-key-label">{key}</Box>
                                <Box>{value}</Box>
                              </div>
                            ))}
                          </div>
                          <div>
                            <Box variant="h4">Relationships</Box>
                            {item.entities_and_relationships.relationships.map((rel: string, idx: number) => (
                              <Box key={idx}>• {rel}</Box>
                            ))}
                          </div>
                        </SpaceBetween>
                      </ExpandableSection>

                      <ExpandableSection headerText="Access Patterns">
                        <ColumnLayout columns={2} variant="text-grid">
                          <div>
                            <Box variant="h4">Read Patterns</Box>
                            {item.access_patterns.read_patterns.map((pattern: string, idx: number) => (
                              <Box key={idx}>• {pattern}</Box>
                            ))}
                          </div>
                          <div>
                            <Box variant="h4">Write Patterns</Box>
                            {item.access_patterns.write_patterns.map((pattern: string, idx: number) => (
                              <Box key={idx}>• {pattern}</Box>
                            ))}
                          </div>
                        </ColumnLayout>
                      </ExpandableSection>

                      <ExpandableSection headerText="Performance & Scale Requirements">
                        <SpaceBetween direction="vertical" size="s">
                          <ColumnLayout columns={2} variant="text-grid">
                            <div>
                              <Box variant="awsui-key-label">Data Growth</Box>
                              <Box>{item.performance_and_scale.data_growth}</Box>
                            </div>
                            <div>
                              <Box variant="awsui-key-label">Read/Write Ratio</Box>
                              <Box>{item.performance_and_scale.read_write_ratio}</Box>
                            </div>
                            <div>
                              <Box variant="awsui-key-label">Scalability Needs</Box>
                              <Box>{item.performance_and_scale.scalability_needs}</Box>
                            </div>
                            <div>
                              <Box variant="awsui-key-label">Regional Requirements</Box>
                              <Box>{item.performance_and_scale.regional_requirements}</Box>
                            </div>
                          </ColumnLayout>
                          <div>
                            <Box variant="h4">Performance Requirements</Box>
                            {item.performance_and_scale.performance_requirements.map((req, idx) => (
                              <Box key={idx}>• {req}</Box>
                            ))}
                          </div>
                        </SpaceBetween>
                      </ExpandableSection>

                      <ExpandableSection headerText="Expected Elements & Key Concepts">
                        <ColumnLayout columns={2} variant="text-grid">
                          <div>
                            <Box variant="h4">Expected Elements</Box>
                            {item.expected_elements.map((element, idx) => (
                              <Box key={idx}>• {element}</Box>
                            ))}
                          </div>
                          <div>
                            <Box variant="h4">Key Concepts</Box>
                            {item.key_concepts_should_include.map((concept, idx) => (
                              <Box key={idx}>• {concept}</Box>
                            ))}
                          </div>
                        </ColumnLayout>
                      </ExpandableSection>
                    </SpaceBetween>
                  )
                }
              ]
            }}
            cardsPerRow={[{ cards: 1 }]}
            items={scenarios}
          />
        </ContentLayout>
      );
    }

    // Dashboard content
    return (
      <ContentLayout>
        <SpaceBetween direction="vertical" size="l">
          <Container
            header={
              <Header
                variant="h2"
                actions={
                  <SpaceBetween direction="horizontal" size="s">
                    <Select
                      selectedOption={selectedScenario}
                      onChange={({ detail }) => setSelectedScenario(detail.selectedOption as { label: string; value: string })}
                      options={scenarios.map(s => ({ label: s.name, value: s.name }))}
                      placeholder="Choose scenario"
                    />
                    <Button
                      variant="primary"
                      loading={isRunning}
                      onClick={runEvaluation}
                    >
                      Run Evaluation
                    </Button>
                  </SpaceBetween>
                }
              >
                Evaluation Controls
              </Header>
            }
          >
            <SpaceBetween direction="vertical" size="s">
              <Box>Configure and run DynamoDB guidance evaluations using scenario: <strong>{selectedScenario.label}</strong></Box>
              {(() => {
                const scenario = scenarios.find(s => s.name === selectedScenario.value);
                return scenario ? (
                  <Container>
                    <SpaceBetween direction="vertical" size="xs">
                      <Box>{scenario.description}</Box>
                      <ColumnLayout columns={3} variant="text-grid">
                        <div>
                          <Box variant="awsui-key-label">Complexity</Box>
                          <Badge color={scenario.complexity === 'advanced' ? 'red' : 'blue'}>
                            {scenario.complexity}
                          </Badge>
                        </div>
                        <div>
                          <Box variant="awsui-key-label">User Base</Box>
                          <Box>{scenario.performance_and_scale.user_base}</Box>
                        </div>
                        <div>
                          <Box variant="awsui-key-label">Transaction Volume</Box>
                          <Box>{scenario.performance_and_scale.transaction_volume}</Box>
                        </div>
                      </ColumnLayout>
                      <Box>
                        <Link href="#" onFollow={() => setActiveHref('/scenarios')}>
                          View full scenario details →
                        </Link>
                      </Box>
                    </SpaceBetween>
                  </Container>
                ) : null;
              })()}
            </SpaceBetween>
          </Container>

          {isRunning && (
            <Container>
              <ProgressBar
                status="in-progress"
                value={progress}
                label="Running DynamoDB evaluation..."
                description={`Analyzing guidance quality across 5 dimensions (${Math.round(progress)}% complete)`}
              />
            </Container>
          )}

          {results.length === 0 ? (
            <Box textAlign="center" color="inherit">
              <b>No evaluations yet</b>
              <Box variant="p" color="inherit">
                Click "Run Evaluation" to start testing DynamoDB guidance quality.
              </Box>
            </Box>
          ) : (
            <SpaceBetween direction="vertical" size="l">
              {results.map((result, index) => renderEvaluationResult(result, index))}
            </SpaceBetween>
          )}
        </SpaceBetween>
      </ContentLayout>
    );
  };

  return (
    <>
      <TopNavigation
        identity={{
          href: "/",
          title: "DynamoDB MCP Evaluations"
        }}
        utilities={[
          {
            type: "button",
            text: "Documentation",
            href: "https://github.com/awslabs/mcp/tree/main/src/dynamodb-mcp-server",
            external: true
          },
          {
            type: "menu-dropdown",
            text: "Settings",
            items: [
              { id: "profile", text: "User Profile" },
              { id: "preferences", text: "Preferences" },
              { id: "signout", text: "Sign Out" }
            ]
          }
        ]}
      />
      <AppLayout
        navigation={
          <SideNavigation
            activeHref={activeHref}
            header={{ href: "/", text: "DynamoDB Evals" }}
            onFollow={event => {
              if (!event.detail.external) {
                event.preventDefault();
                setActiveHref(event.detail.href);
              }
            }}
            items={[
              { type: "link", text: "Dashboard", href: "/dashboard" },
              { type: "link", text: "Scenarios", href: "/scenarios" },
              { type: "link", text: "Prompt Editor", href: "/prompt-editor" },
              { type: "link", text: "History", href: "/history" },
              { type: "divider" },
              { 
                type: "link", 
                text: "Settings", 
                href: "/settings",
                info: <Link variant="info">Info</Link>
              }
            ]}
          />
        }
        tools={
          <HelpPanel
            header={<h2>DynamoDB Evaluation Help</h2>}
          >
            <SpaceBetween direction="vertical" size="m">
              <div>
                <h3>Evaluation Dimensions</h3>
                <ul>
                  <li><strong>Completeness:</strong> Coverage of all scenario elements</li>
                  <li><strong>Technical Accuracy:</strong> Correctness of DynamoDB recommendations</li>
                  <li><strong>Access Pattern Coverage:</strong> Optimization of query patterns</li>
                  <li><strong>Scalability:</strong> Planning for growth and performance</li>
                  <li><strong>Cost Optimization:</strong> Cost-efficient strategies</li>
                </ul>
              </div>
              <div>
                <h3>Score Ranges</h3>
                <ul>
                  <li><Badge color="green">9-10:</Badge> Excellent</li>
                  <li><Badge color="blue">7-8:</Badge> Good</li>
                  <li><Badge color="red">1-6:</Badge> Needs Improvement</li>
                </ul>
              </div>
            </SpaceBetween>
          </HelpPanel>
        }
        content={renderContent()}
      />
      
      <Modal
        onDismiss={() => setModalVisible(false)}
        visible={modalVisible}
        size="max"
        header={modalTitle}
      >
        <div style={{ maxHeight: '70vh', overflow: 'auto', padding: '16px' }}>
          <ReactMarkdown 
            remarkPlugins={[remarkGfm]}
            components={{
              table: ({children}) => <table style={{borderCollapse: 'collapse', width: '100%', margin: '16px 0'}}>{children}</table>,
              th: ({children}) => <th style={{border: '1px solid #ddd', padding: '8px', backgroundColor: '#f5f5f5', fontWeight: 'bold'}}>{children}</th>,
              td: ({children}) => <td style={{border: '1px solid #ddd', padding: '8px'}}>{children}</td>
            }}
          >
            {modalContent}
          </ReactMarkdown>
        </div>
      </Modal>
    </>
  );
};

export default App;
